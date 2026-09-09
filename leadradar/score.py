"""Puanlama ve zenginlestirme — orijinal 'OPPORTUNITY SCORING — STRICT GUARDRAILS'
kurallarinin birebir kod karsiligi.

Kurallar (orijinal sistem mesajindan):
  1. Web sitesi yok + kaynakta site listelenmemis  -> High
  2. Web sitesi var: en az 2 NESNEL engel dogrulanirsa -> High, yoksa en fazla Medium
  3. Sezgisel bulgular ([HEURISTIC]) tek baslarina asla High uretmez
  4. HTTPS var + calisan iletisim + bariz hata yok -> Medium veya Low
  5. why_lead kanita dayali olmali (1-2 kisa olgusal neden)

Ek karar (belgelendi): resmi site yerine yalnizca Facebook/Instagram sayfasi olan
isletmeler "resmi web sitesi yok" sayilir -> High. (Orijinal akista bu durum
"zayif web varligi" olarak zaten oncelikli hedefti.)
"""

from datetime import datetime


def _freshness(lead, audit):
    parts = []
    if audit:
        if audit.get("copyright_year"):
            parts.append(f"Sitedeki telif yılı: {audit['copyright_year']}")
        if audit.get("last_modified"):
            parts.append(f"Sunucu Last-Modified: {audit['last_modified']}")
    if lead.get("osm_check_date"):
        parts.append(f"OSM kontrol tarihi: {lead['osm_check_date']}")
    return "; ".join(parts) if parts else None


def _operating_status(lead, audit):
    if audit and audit.get("loads"):
        return "Aktif görünüyor (web sitesi erişilebilir)"
    signals = []
    if lead.get("phone"):
        signals.append("telefon kaydı")
    if lead.get("opening_hours"):
        signals.append("çalışma saatleri kaydı")
    if signals:
        return f"Muhtemelen aktif ({' ve '.join(signals)} mevcut) — teyit önerilir"
    if audit and not audit.get("loads"):
        return "Doğrulanamadı — web sitesi erişilemiyor, aramadan önce teyit edin"
    return "Doğrulanamadı — kayıt mevcut ancak güncellik teyidi önerilir"


def score_lead(lead, audit):
    """Lead + denetim sonucundan skor, gerekce ve rapor alanlarini uretir."""
    tier = lead.get("website_tier", "has")
    issues, heuristics = [], []
    tech = []

    if tier == "none":
        score = "High"
        issues.append("Web sitesi kaydı yok (kaynak: OpenStreetMap işletme kaydı)")
        why = "Web sitesi yok — birebir hedef profil; sıfırdan site satışı için en güçlü aday."
    elif tier == "social":
        score = "High"
        issues.append(f"Resmî web sitesi yok; yalnızca sosyal medya sayfası: {lead.get('website')}")
        why = "Gerçek bir web sitesi yerine yalnızca sosyal medya sayfası var — profesyonel site ihtiyacı net."
    else:
        issues = list(audit["objective_issues"])
        heuristics = list(audit["heuristic_issues"])
        tech = list(audit["tech_signals"])
        blockers = audit["blocker_count"]
        if blockers >= 2:
            score = "High"
        elif blockers == 1:
            score = "Medium"
        else:
            score = "Medium" if len(heuristics) >= 2 else "Low"

        if issues:
            why = "Doğrulanan sorunlar: " + "; ".join(issues[:2])
        elif heuristics:
            why = "Site çalışıyor; yalnızca sezgisel iyileştirme fırsatları var (ayrıntı: sezgisel değerlendirme)."
        else:
            why = "Site teknik olarak sağlıklı görünüyor — düşük öncelikli aday."

    return {
        "opportunity_score": score,
        "website_issues": issues,
        "heuristic_assessment": heuristics,
        "tech_signals": tech,
        "why_lead": why,
        "freshness_signal": _freshness(lead, audit),
        "operating_status": _operating_status(lead, audit),
    }


def build_contact_plan(lead, audit):
    """'Nasil iletisime gecebilirim?' — kanallari oncelik sirasiyla listeler."""
    plan = []
    phone = lead.get("phone") or (audit and next(iter(audit.get("phones_on_site", [])), None))
    if phone:
        plan.append(f"1. Telefon (en hızlı kanal): {phone}")
    emails = (audit or {}).get("emails") or []
    if emails:
        plan.append(f"{len(plan) + 1}. E-posta: {', '.join(emails[:2])}")
    if audit and audit.get("contact_links"):
        plan.append(f"{len(plan) + 1}. Sitedeki iletişim sayfası: {audit['contact_links'][0]}")
    socials = (audit or {}).get("social_links") or []
    if lead.get("website_tier") == "social" and lead.get("website"):
        socials = [lead["website"]] + socials
    if socials:
        plan.append(f"{len(plan) + 1}. Sosyal medya (DM): {socials[0]}")
    if lead.get("address"):
        plan.append(f"{len(plan) + 1}. Yerinde ziyaret: {lead['address']}")
    if not plan:
        plan.append(f"1. OSM kaydından başlayın: {lead.get('source_links')} (telefon/e-posta yok — yerinde ziyaret gerekebilir)")
    return plan


def build_outreach_tip(lead, scored):
    """Gorusme acilisi icin kisa, kanita dayali Turkce oneri."""
    name = lead["business_name"]
    score = scored["opportunity_score"]
    issues = scored["website_issues"]
    if lead.get("website_tier") == "none":
        return (f"Açılış önerisi: \"{name} için arama yaptığımda web sitenizi bulamadım; "
                f"müşterilerinizin çoğu sizi internette arıyor. Size hızlıca kurulabilecek, "
                f"telefonla uyumlu bir tanıtım sitesi önerebilirim.\"")
    if lead.get("website_tier") == "social":
        return (f"Açılış önerisi: \"{name} şu an yalnızca sosyal medyada görünüyor; "
                f"Google'da sizi arayanlar resmî bir siteye ulaşamıyor. Sosyal hesabınızı "
                f"besleyen basit bir resmî site büyük fark yaratır.\"")
    if issues:
        top = issues[0].split("—")[0].strip().rstrip(":")
        return (f"Açılış önerisi: \"Sitenize baktım; öne çıkan konu şu: {top}. "
                f"Bu, müşteri kaybettiren teknik bir sorun — kısa sürede çözülebilir.\"")
    if score == "Low":
        return ("Açılış önerisi: Sitesi sağlıklı; acil satış açısı yok. İleride yenileme/"
                "SEO ihtiyacı için nazik bir tanışma mesajı uygun olur.")
    return "Açılış önerisi: Sezgisel bulgulardan birini (ör. güncellik) nazikçe gündeme getirin."
