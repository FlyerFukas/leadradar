# -*- coding: utf-8 -*-
# LeadRadar — yerel işletme lead keşif ve zenginleştirme sistemi
# Copyright (c) 2026 Furkan Akduman · https://github.com/FlyerFukas
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
#
# Ticari olmayan kullanım serbesttir (bkz. LICENSE).
# İşletmeler ve her türlü ticari kullanım ayrı, ücretli lisans gerektirir.
# Ayrıntı ve iletişim: COMMERCIAL.md
"""LeadRadar — uctan uca haftalik lead calistirmasi.

Kullanim:
    py run.py                     # tam calistirma (kesif -> denetim -> PDF)
    py run.py --limit 10          # rapora secilecek aday sayisi
    py run.py --week 30           # rotasyon haftasini elle sec (test icin)
    py run.py --config config.json

Boru hatti (orijinal n8n akisiyla ayni sira):
  Rotasyon -> Kesif (Overpass) -> Parmak izi -> Gorulmusleri getir (SQLite)
  -> Yeni olanlari sec -> Web sitesi denetimi -> Puanlama (guardrails)
  -> SQLite'a yaz -> PDF raporu uret
"""

import argparse
import csv
import json
import locale
import os
import sys
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from leadradar import audit as audit_mod
from leadradar import discover as discover_mod
from leadradar import report as report_mod
from leadradar import score as score_mod
from leadradar import store as store_mod
from leadradar.config import load_config
from leadradar.rotation import compute_rotation


def main():
    parser = argparse.ArgumentParser(description="LeadRadar haftalik lead calistirmasi")
    parser.add_argument("--limit", type=int, default=None, help="rapora secilecek aday sayisi")
    parser.add_argument("--week", type=int, default=None, help="rotasyon haftasi (elle)")
    parser.add_argument("--config", default=os.path.join(BASE_DIR, "config.json"))
    parser.add_argument("--run-config", default=None,
                        help="panelden gelen manuel secim (sehir/semt/sektor) JSON dosyasi")
    parser.add_argument("--db", default=os.path.join(BASE_DIR, "data", "leads.db"))
    parser.add_argument("--out-dir", default=os.path.join(BASE_DIR, "output"))
    args = parser.parse_args()

    try:
        locale.setlocale(locale.LC_TIME, "Turkish_Turkey.1254")
    except locale.Error:
        pass

    cfg = load_config(args.config)
    if args.limit:
        cfg["target_leads"] = args.limit
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.db), exist_ok=True)

    # Panelden gelen manuel secim (varsa)
    run_conf = None
    if args.run_config and os.path.exists(args.run_config):
        with open(args.run_config, encoding="utf-8") as f:
            run_conf = json.load(f)

    now = datetime.now()
    print("=" * 62)
    print("LeadRadar — Yerel İşletme Lead Radarı")
    print("=" * 62)

    # 1) Rotasyon / manuel secim
    if run_conf:
        cfg["city"] = run_conf.get("city") or cfg["city"]
        admin = str(run_conf.get("admin_level")
                    or cfg["city_catalog"].get(cfg["city"], "6|8"))
        cfg["city_admin_levels"] = admin  # semt sorgulari da bu sehir seviyesini kullanir
        if "firecrawl" in run_conf:
            cfg["firecrawl"]["enabled"] = bool(run_conf["firecrawl"])
        if run_conf.get("target_leads"):
            cfg["target_leads"] = int(run_conf["target_leads"])
        sectors = run_conf.get("sectors") or list(cfg["category_osm"].keys())[:4]
        districts = [d.strip() for d in (run_conf.get("districts") or []) if d.strip()]
        rotation = {
            "week_number": 0,
            "categories": sectors,
            "areas": districts,
            "whole_city": len(districts) == 0,
            "city": cfg["city"],
            "admin_level": admin,
            "hint": (f"Manuel seçim: {cfg['city']} / "
                     f"{'tüm şehir' if not districts else ', '.join(districts)} / "
                     f"sektörler: {', '.join(sectors)}"),
        }
        print(f"[1/7] {rotation['hint']}")
    else:
        rotation = compute_rotation(cfg, now=now, week_override=args.week)
        print(f"[1/7] Rotasyon: hafta {rotation['week_number']} — {rotation['hint']}")

    # 2) Kesif (orijinal: AI Agent — Discover Fresh + Firecrawl /search)
    print("[2/7] Keşif başlıyor (OpenStreetMap Overpass API)...")
    raw_leads, defter = discover_mod.discover(cfg, rotation)
    pool = discover_mod.prioritize(raw_leads, cfg)
    print(f"      Toplam {len(raw_leads)} aday bulundu; öncelik sırasına göre {len(pool)} tanesi havuza alındı.")

    # 3-4) Parmak izi + gorulmusleri ele (orijinal: Compute Fingerprint,
    #      Fetch Seen Fingerprints, Filter Unseen Top 10)
    conn = store_mod.connect(args.db)
    seen = store_mod.fetch_seen_fingerprints(conn)
    unseen = [l for l in pool if l["fingerprint"] not in seen]
    print(f"[3/7] Tekilleştirme: {len(seen)} kayıtlı parmak izi; havuzdan {len(unseen)} yeni aday çıktı.")
    selected = discover_mod.select_final(unseen, cfg)
    n_none = sum(1 for l in selected if l["website_tier"] == "none")

    # Ham veri defterine boru hattindaki akibeti isle
    fp_havuz = {l["fingerprint"] for l in pool}
    fp_secili = {l["fingerprint"] for l in selected}
    for k in defter:
        fp = k.get("parmak_izi")
        if k["asama"] == "ham_kayit" and k["eleme_sebebi"]:
            k["asama"] = "elendi"
        elif fp and fp in fp_secili:
            k["asama"] = "rapora_secildi"
        elif fp and fp in seen:
            k["asama"] = "elendi"
            k["eleme_sebebi"] = "onceki_haftalarda_raporlandi"
        elif fp and fp in fp_havuz:
            k["asama"] = "oncelik_havuzunda"
            k["eleme_sebebi"] = "havuzda_kaldi_rapora_girmedi"
        elif k["asama"] == "cerceveye_girdi":
            k["eleme_sebebi"] = "havuz_disinda_kaldi"
    print(f"[4/7] Seçim: {len(selected)} aday ({n_none} tanesi web sitesiz, {len(selected) - n_none} tanesi siteli).")

    # 5) Zenginlestirme + denetim + puanlama (orijinal: AI Agent — enrichment)
    print("[5/7] Web sitesi denetimi ve puanlama...")

    # Istege bagli Firecrawl istemcisi (puan/yorum + guclu tarama)
    fc_client = None
    try:
        from leadradar import firecrawl_client as fc_mod
        fc_client = fc_mod.maybe_client(cfg)
    except Exception as exc:
        print(f"      Firecrawl atlandı: {exc}")

    enriched = []
    for idx, lead in enumerate(selected, 1):
        website_note = lead.get("website") or "site yok"
        print(f"      ({idx}/{len(selected)}) {lead['business_name']} — {website_note}")

        # Firecrawl: rehberlerden puan/yorum zenginlestirme
        if fc_client and cfg["firecrawl"].get("enrich_ratings"):
            try:
                rating = fc_mod.enrich_rating(fc_client, lead, cfg)
                if rating["public_rating"] or rating["review_count"]:
                    lead["public_rating"] = rating["public_rating"]
                    lead["review_count"] = rating["review_count"]
                    lead["rating_source"] = rating["rating_source"]
                    print(f"        Puan: {rating['public_rating']} / {rating['review_count']} yorum")
            except Exception as exc:
                print(f"        Puan zenginleştirme atlandı: {exc}")

        audit_result = None
        if lead["website_tier"] in ("has", "http"):
            scrape_fc = fc_client if cfg["firecrawl"].get("scrape_sites") else None
            try:
                audit_result = audit_mod.audit_website(lead["website"], cfg, firecrawl_client=scrape_fc)
            except Exception as exc:  # tek site tum calistirmayi durdurmasin
                print(f"        Denetim hatası: {exc}")
                audit_result = {
                    "input_url": lead["website"], "objective_issues": [f"Denetim tamamlanamadı: {type(exc).__name__}"],
                    "heuristic_issues": [], "tech_signals": [], "blocker_count": 1,
                    "loads": False, "https": False, "ssl_error": False,
                    "phones_on_site": [], "emails": [], "contact_links": [],
                    "broken_contact_links": [], "booking_links": [], "external_booking": [],
                    "broken_booking_links": [], "social_links": [], "viewport": None,
                    "final_url": None, "http_status": None, "title": None,
                    "copyright_year": None, "last_modified": None, "generator": None,
                    "blank": False, "redirect_loop": False, "has_mailto": False,
                }
            time.sleep(cfg["request_delay_sec"])
        scored = score_mod.score_lead(lead, audit_result)
        enriched.append({
            "lead": lead,
            "audit": audit_result,
            "scored": scored,
            "contact_plan": score_mod.build_contact_plan(lead, audit_result),
            "outreach_tip": score_mod.build_outreach_tip(lead, scored),
        })

    # Istege bagli yapay zeka cilasi
    if cfg["ai"]["enabled"]:
        try:
            from leadradar import ai_polish
            print("      Yapay zeka cilası uygulanıyor...")
            ai_polish.polish(enriched, cfg)
        except Exception as exc:
            print(f"      Yapay zeka cilası atlandı: {exc}")

    # 6) Kayit (orijinal: Postgres — Insert Lead)
    week_of = now.strftime("%Y-%m-%d")
    for item in enriched:
        lead, scored, audit_result = item["lead"], item["scored"], item["audit"]
        store_mod.insert_lead(conn, {
            "fingerprint": lead["fingerprint"],
            "business_name": lead["business_name"],
            "category": lead["category"],
            "address": lead["address"],
            "phone": lead["phone"],
            "website": lead["website"],
            "public_rating": lead.get("public_rating"),
            "review_count": lead.get("review_count"),
            "website_issues": "; ".join(scored["website_issues"]) or None,
            "heuristic_assessment": "; ".join(scored["heuristic_assessment"]) or None,
            "services_listed": lead.get("services_listed"),
            "tech_signals": ", ".join(scored["tech_signals"]) or None,
            "freshness_signal": scored["freshness_signal"],
            "operating_status": scored["operating_status"],
            "opportunity_score": scored["opportunity_score"],
            "why_lead": scored["why_lead"],
            "source_links": lead["source_links"],
            "week_of": week_of,
            "discovered_at": now.isoformat(timespec="seconds"),
            "district": lead["district"],
            "emails": ", ".join((audit_result or {}).get("emails") or []) or None,
        })
    conn.commit()
    print(f"[6/7] Veritabanına yazıldı ({store_mod.count_leads(conn)} toplam kayıt): {args.db}")
    if fc_client:
        print(f"      Firecrawl bu çalıştırmada ~{fc_client.credits_used} kredi kullandı.")

    # 7) PDF raporu (orijinal: Build Email HTML + Gmail yerine)
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for item in enriched:
        counts[item["scored"]["opportunity_score"]] += 1
    run_info = {
        "date": now,
        "city": cfg["city"],
        "week_number": rotation["week_number"],
        "categories": rotation["categories"],
        "areas": rotation["areas"] if rotation["areas"] else ["Tüm şehir"],
        "discovered": len(raw_leads),
        "unseen": len(unseen),
        "score_summary": f"YÜKSEK: {counts['High']} • ORTA: {counts['Medium']} • DÜŞÜK: {counts['Low']}",
    }
    # Dosya adina tarih + saat: ayni gun tekrar calistirinca eskisi SILINMEZ,
    # her calistirma ayri dosya olur.
    stamp = now.strftime("%Y-%m-%d_%H-%M")
    city_slug = "".join(c for c in cfg["city"] if c.isalnum()) or "Sehir"
    pdf_path = os.path.join(args.out_dir, f"LeadRadar_Lead_Raporu_{city_slug}_{stamp}.pdf")
    report_mod.build_leads_pdf(pdf_path, run_info, enriched)
    print(f"[7/7] PDF raporu hazır: {pdf_path}")

    # Ham veri dokumu (seffaflik/ariza ayiklama icin)
    json_path = os.path.join(args.out_dir, f"LeadRadar_calistirma_{city_slug}_{stamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_info": {**run_info, "date": now.isoformat(timespec="seconds")},
                "leads": [
                    {"lead": it["lead"], "audit": it["audit"], "scored": it["scored"],
                     "contact_plan": it["contact_plan"], "outreach_tip": it["outreach_tip"]}
                    for it in enriched
                ],
            },
            f, ensure_ascii=False, indent=2,
        )
    print(f"      Ham veri: {json_path}")

    # --- Taranan ham verinin tamami: ayri CSV + JSON ambari ---
    ozet = {}
    for k in defter:
        anahtar = k["eleme_sebebi"] or k["asama"]
        ozet[anahtar] = ozet.get(anahtar, 0) + 1

    csv_path = os.path.join(args.out_dir, f"LeadRadar_TarananVeri_{city_slug}_{stamp}.csv")
    alanlar = ["osm_type", "osm_id", "enlem", "boylam", "isletme_adi", "kategori",
               "arama_bolgesi", "adres", "telefon", "website", "website_durumu",
               "acilis_saatleri", "osm_kontrol_tarihi", "parmak_izi",
               "asama", "eleme_sebebi", "osm_baglantisi", "etiket_sayisi", "ham_etiketler"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, delimiter=";")
        w.writeheader()
        for k in defter:
            t = k["ham_etiketler"] or {}
            site = t.get("website") or t.get("contact:website") or t.get("url")
            w.writerow({
                "osm_type": k["osm_type"], "osm_id": k["osm_id"],
                "enlem": k["enlem"], "boylam": k["boylam"],
                "isletme_adi": k["isletme_adi"], "kategori": k["kategori"],
                "arama_bolgesi": k["arama_bolgesi"],
                "adres": " ".join(x for x in (t.get("addr:street"), t.get("addr:housenumber"),
                                              t.get("addr:postcode"), t.get("addr:city")) if x) or None,
                "telefon": t.get("phone") or t.get("contact:phone"),
                "website": site,
                "website_durumu": discover_mod.website_tier(site) if k["kategori"] else None,
                "acilis_saatleri": t.get("opening_hours"),
                "osm_kontrol_tarihi": t.get("check_date") or t.get("survey:date"),
                "parmak_izi": k["parmak_izi"],
                "asama": k["asama"], "eleme_sebebi": k["eleme_sebebi"],
                "osm_baglantisi": f"https://www.openstreetmap.org/{k['osm_type']}/{k['osm_id']}",
                "etiket_sayisi": len(t),
                "ham_etiketler": json.dumps(t, ensure_ascii=False),
            })

    ambar_path = os.path.join(args.out_dir, f"LeadRadar_TarananVeri_{city_slug}_{stamp}.json")
    with open(ambar_path, "w", encoding="utf-8") as f:
        json.dump({
            "calistirma": {**run_info, "date": now.isoformat(timespec="seconds")},
            "veri_kaynagi": {
                "ad": "OpenStreetMap",
                "erisim": "Overpass API",
                "lisans": "ODbL 1.0 (https://www.openstreetmap.org/copyright)",
                "sorgu_turu": "idari sinir poligonu icinde etiket filtresi",
                "cekilme_zamani": now.isoformat(timespec="seconds"),
            },
            "ozet": {
                "ham_kayit_sayisi": len(defter),
                "asama_dagilimi": ozet,
                "cerceveye_giren": sum(1 for k in defter if k["asama"] != "elendi"),
                "rapora_secilen": len(selected),
            },
            "kayitlar": defter,
        }, f, ensure_ascii=False, indent=2)

    print(f"      Taranan veri (CSV): {csv_path}")
    print(f"      Taranan veri (JSON): {ambar_path}")
    print(f"      Ham kayit: {len(defter)} | asama dagilimi: {ozet}")
    conn.close()
    return pdf_path


if __name__ == "__main__":
    main()
