"""PDF lead raporu — orijinal 'Build Email HTML' + 'Gmail' adimlarinin yerine gecer.

Rapor yapisi (kullanicinin istedigi sirayla, her aday icin):
  1. Parametreler (kategori, semt, skor, durum, tazelik, teknoloji...)
  2. Bilgiler ve iletisim (adres, telefon, e-posta, site, kaynak, iletisim plani)
  3. Web sitesi hata ve sorunlari (nesnel + sezgisel bulgular, teknik denetim tablosu)
"""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

NAVY = colors.HexColor("#1a1a2e")
LIGHT = colors.HexColor("#f4f4f8")
GRID = colors.HexColor("#d9d9e3")
SCORE_COLORS = {
    "High": colors.HexColor("#1b7f3b"),
    "Medium": colors.HexColor("#d97706"),
    "Low": colors.HexColor("#6b7280"),
}
SCORE_TR = {"High": "YÜKSEK", "Medium": "ORTA", "Low": "DÜŞÜK"}

_FONTS_READY = False
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def _register_fonts():
    """Turkce karakterler icin Windows TTF fontlarini kaydeder."""
    global _FONTS_READY, FONT, FONT_BOLD
    if _FONTS_READY:
        return
    candidates = [
        (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf"),
    ]
    for regular, bold in candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("NSans", regular))
            pdfmetrics.registerFont(TTFont("NSans-Bold", bold))
            FONT, FONT_BOLD = "NSans", "NSans-Bold"
            break
    _FONTS_READY = True


def _styles():
    base = dict(fontName=FONT, textColor=colors.HexColor("#222230"))
    return {
        "title": ParagraphStyle("t", fontSize=24, leading=30, fontName=FONT_BOLD, textColor=colors.white),
        "subtitle": ParagraphStyle("st", fontSize=11, leading=15, fontName=FONT, textColor=colors.HexColor("#c9c9dd")),
        "h1": ParagraphStyle("h1", fontSize=16, leading=20, fontName=FONT_BOLD, textColor=NAVY, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontSize=12, leading=16, fontName=FONT_BOLD, textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("b", fontSize=9.5, leading=13.5, **base),
        "small": ParagraphStyle("s", fontSize=8.5, leading=12, fontName=FONT, textColor=colors.HexColor("#555566")),
        "cell": ParagraphStyle("c", fontSize=9, leading=12.5, **base),
        "cellb": ParagraphStyle("cb", fontSize=9, leading=12.5, fontName=FONT_BOLD, textColor=NAVY),
        "issue": ParagraphStyle("i", fontSize=9.5, leading=13.5, fontName=FONT, textColor=colors.HexColor("#8a1f1f"), leftIndent=4),
        "heur": ParagraphStyle("hh", fontSize=9.5, leading=13.5, fontName=FONT, textColor=colors.HexColor("#8a6d1f"), leftIndent=4),
        "ok": ParagraphStyle("ok", fontSize=9.5, leading=13.5, fontName=FONT, textColor=colors.HexColor("#1b7f3b"), leftIndent=4),
    }


def _v(value, fallback="—"):
    if value is None or value == "" or value == []:
        return fallback
    if isinstance(value, list):
        return "; ".join(str(x) for x in value)
    return str(value)


def _kv_table(rows, st, col1=48 * mm, col2=122 * mm):
    data = [[Paragraph(k, st["cellb"]), Paragraph(_v(v), st["cell"])] for k, v in rows]
    table = Table(data, colWidths=[col1, col2])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _header_bar(title_text, subtitle_text, st):
    inner = Table(
        [[Paragraph(title_text, st["title"])], [Paragraph(subtitle_text, st["subtitle"])]],
        colWidths=[170 * mm],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 14),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
    ]))
    return inner


def _score_badge(score, st):
    color = SCORE_COLORS.get(score, colors.grey)
    label = SCORE_TR.get(score, score or "—")
    badge = Table([[Paragraph(
        f'<font color="white"><b>FIRSAT SKORU: {label}</b></font>',
        ParagraphStyle("badge", fontSize=10, leading=13, fontName=FONT_BOLD),
    )]], colWidths=[60 * mm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return badge


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.HexColor("#888899"))
    canvas.drawString(18 * mm, 12 * mm, "LeadRadar — Yerel İşletme Lead Radarı")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Sayfa {doc.page}")
    canvas.restoreState()


def _score_sort_key(lead):
    order = {"High": 0, "Medium": 1, "Low": 2}
    return order.get(lead["scored"]["opportunity_score"], 3)


def build_leads_pdf(out_path, run_info, enriched_leads):
    """enriched_leads: [{'lead': ..., 'audit': ... | None, 'scored': ...,
    'contact_plan': [...], 'outreach_tip': str}, ...]"""
    _register_fonts()
    st = _styles()
    leads = sorted(enriched_leads, key=_score_sort_key)  # orijinal e-posta sirasi: High -> Low

    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=20 * mm,
        title="LeadRadar Haftalık Lead Raporu",
    )
    story = []

    # ---------- Kapak / calisma ozeti ----------
    week_str = run_info["date"].strftime("%d %B %Y")
    story.append(_header_bar(
        "LeadRadar — Haftalık Lead Raporu",
        f"{week_str} haftası &nbsp;•&nbsp; {len(leads)} yeni aday &nbsp;•&nbsp; Şehir: {run_info['city']}",
        st,
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Çalıştırma Parametreleri", st["h1"]))
    story.append(_kv_table([
        ("Tarih", run_info["date"].strftime("%d.%m.%Y %H:%M")),
        ("Rotasyon haftası", str(run_info["week_number"])),
        ("Bu haftanın kategorileri", ", ".join(run_info["categories"])),
        ("Bu haftanın semtleri", ", ".join(run_info["areas"])),
        ("Keşfedilen aday sayısı", str(run_info["discovered"])),
        ("Daha önce görülmemiş (yeni)", str(run_info["unseen"])),
        ("Bu rapora seçilen", str(len(leads))),
        ("Veri kaynağı", "OpenStreetMap (Overpass API) + adayların kendi web siteleri"),
        ("Skor dağılımı", run_info["score_summary"]),
    ], st))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Özet Tablo (skora göre sıralı)", st["h1"]))
    head = ["#", "İşletme", "Kategori", "Semt", "Skor", "Site"]
    rows = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("th", fontSize=9, leading=12, fontName=FONT_BOLD, textColor=colors.white)) for h in head]]
    for i, item in enumerate(leads, 1):
        lead, scored = item["lead"], item["scored"]
        rows.append([
            Paragraph(str(i), st["cell"]),
            Paragraph(_v(lead["business_name"]), st["cell"]),
            Paragraph(_v(lead["category"]), st["cell"]),
            Paragraph(_v(lead["district"]), st["cell"]),
            Paragraph(f'<font color="{SCORE_COLORS[scored["opportunity_score"]].hexval()}"><b>{SCORE_TR[scored["opportunity_score"]]}</b></font>', st["cell"]),
            Paragraph("Var" if lead.get("website") and lead["website_tier"] != "social"
                      else ("Sadece sosyal" if lead["website_tier"] == "social" else "YOK"), st["cell"]),
        ])
    summary = Table(rows, colWidths=[8 * mm, 62 * mm, 28 * mm, 32 * mm, 20 * mm, 20 * mm], repeatRows=1)
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(summary)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Skorlama kuralı: <b>YÜKSEK</b> = web sitesi yok VEYA en az 2 doğrulanmış nesnel engel; "
        "<b>ORTA</b> = 1 nesnel engel ya da birden çok sezgisel bulgu; <b>DÜŞÜK</b> = site sağlıklı. "
        "Sezgisel bulgular tek başına asla YÜKSEK skor üretmez.", st["small"]))

    # ---------- Aday detay sayfalari ----------
    for i, item in enumerate(leads, 1):
        lead, audit, scored = item["lead"], item["audit"], item["scored"]
        story.append(PageBreak())
        story.append(_header_bar(
            f"{i}. {lead['business_name']}",
            f"{lead['category']} • {lead['district']} • {run_info['city']}",
            st,
        ))
        story.append(Spacer(1, 4 * mm))
        story.append(_score_badge(scored["opportunity_score"], st))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(f"<b>Neden aday?</b> {scored['why_lead']}", st["body"]))
        story.append(Spacer(1, 3 * mm))

        # --- 1) PARAMETRELER ---
        story.append(Paragraph("1) Parametreler", st["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.7, color=GRID))
        story.append(Spacer(1, 2 * mm))
        story.append(_kv_table([
            ("Kategori", lead.get("category")),
            ("Semt", lead.get("district")),
            ("Fırsat skoru", SCORE_TR.get(scored["opportunity_score"])),
            ("Web sitesi durumu", {
                "none": "Web sitesi YOK",
                "social": "Sadece sosyal medya sayfası",
                "http": "Var — güvensiz (http)",
                "has": "Var",
            }.get(lead.get("website_tier"), "—")),
            ("Faaliyet durumu", scored.get("operating_status")),
            ("Güncellik sinyali", scored.get("freshness_signal")),
            ("Teknoloji sinyalleri", scored.get("tech_signals")),
            ("Listelenen hizmetler", lead.get("services_listed")),
            ("Çalışma saatleri (OSM)", lead.get("opening_hours")),
            ("Halka açık puan / yorum sayısı",
             (f"{lead.get('public_rating')} / {_v(lead.get('review_count'), '?')} yorum"
              + (" (Firecrawl)" if lead.get("rating_source") else ""))
             if lead.get("public_rating") or lead.get("review_count")
             else "Bulunamadı (rehberde puan yok / Firecrawl kapalı)"),
        ], st))

        # --- 2) BILGILER & ILETISIM ---
        story.append(Paragraph("2) Bilgiler ve İletişim", st["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.7, color=GRID))
        story.append(Spacer(1, 2 * mm))
        emails = (audit or {}).get("emails") or []
        story.append(_kv_table([
            ("İşletme adı", lead.get("business_name")),
            ("Adres", lead.get("address")),
            ("Telefon", lead.get("phone") or _v((audit or {}).get("phones_on_site"), "—")),
            ("E-posta (sitede bulunan)", emails),
            ("Web sitesi", lead.get("website"), ),
            ("Sosyal medya", (audit or {}).get("social_links")),
            ("Kanıt / kaynak linki", lead.get("source_links")),
        ], st))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("<b>Nasıl iletişime geçilir?</b>", st["body"]))
        for line in item["contact_plan"]:
            story.append(Paragraph(line, st["cell"]))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(item["outreach_tip"], st["small"]))

        # --- 3) WEB SITESI HATA & SORUNLARI ---
        story.append(Paragraph("3) Web Sitesi Hata ve Sorunları", st["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.7, color=GRID))
        story.append(Spacer(1, 2 * mm))

        issues = scored["website_issues"]
        heuristics = scored["heuristic_assessment"]
        if lead.get("website_tier") in ("none", "social"):
            for issue in issues:
                story.append(Paragraph("• " + issue, st["issue"]))
            story.append(Paragraph(
                "Denetlenecek bir resmî site olmadığı için teknik denetim uygulanmadı — "
                "bu durumun kendisi en büyük satış fırsatıdır.", st["small"]))
        else:
            if issues:
                story.append(Paragraph("<b>Doğrulanmış (nesnel) sorunlar:</b>", st["body"]))
                for issue in issues:
                    story.append(Paragraph("• " + issue, st["issue"]))
            else:
                story.append(Paragraph("• Nesnel engel bulunamadı — site temel testleri geçti.", st["ok"]))
            if heuristics:
                story.append(Spacer(1, 1.5 * mm))
                story.append(Paragraph("<b>Sezgisel değerlendirme (kanıt değil, izlenim):</b>", st["body"]))
                for h in heuristics:
                    story.append(Paragraph("• " + h, st["heur"]))
            if audit:
                story.append(Spacer(1, 2.5 * mm))
                story.append(Paragraph("<b>Teknik denetim ayrıntısı:</b>", st["body"]))
                story.append(_kv_table([
                    ("Denetlenen adres", audit.get("final_url") or audit.get("input_url")),
                    ("Tarama yöntemi", "Firecrawl (JS destekli)" if audit.get("firecrawl_used") else "Doğrudan (requests)"),
                    ("HTTP durum kodu", audit.get("http_status")),
                    ("HTTPS", "Evet" if audit.get("https") else "HAYIR"),
                    ("SSL sorunu", "Evet" if audit.get("ssl_error") else "Yok"),
                    ("Mobil uyumluluk (viewport)", "Evet" if audit.get("viewport") else ("HAYIR" if audit.get("viewport") is False else "—")),
                    ("Sayfa başlığı", audit.get("title")),
                    ("İletişim linkleri", audit.get("contact_links")),
                    ("Bozuk iletişim linkleri", audit.get("broken_contact_links")),
                    ("Randevu/rezervasyon linkleri", (audit.get("booking_links") or []) + (audit.get("external_booking") or [])),
                    ("Bozuk randevu linkleri", audit.get("broken_booking_links")),
                    ("Nesnel engel sayısı", str(audit.get("blocker_count"))),
                ], st))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return out_path
