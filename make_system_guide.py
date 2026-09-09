"""LeadRadar Sistem Rehberi PDF'ini uretir.

Kullanim:  py make_system_guide.py
Cikti:     docs/LeadRadar_Sistem_Rehberi.pdf
"""

import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from leadradar import report as rpt

NAVY = rpt.NAVY
GRID = rpt.GRID
LIGHT = rpt.LIGHT


def styles():
    rpt._register_fonts()
    st = rpt._styles()
    st["h1"] = ParagraphStyle("gh1", fontSize=17, leading=22, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=8, spaceAfter=6)
    st["h2"] = ParagraphStyle("gh2", fontSize=12.5, leading=17, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=8, spaceAfter=3)
    st["body"] = ParagraphStyle("gb", fontSize=10, leading=14.5, fontName=rpt.FONT,
                                textColor=colors.HexColor("#222230"), spaceAfter=4)
    st["li"] = ParagraphStyle("gli", parent=st["body"], leftIndent=6 * mm, spaceAfter=2)
    st["code"] = ParagraphStyle("gc", fontSize=9, leading=13, fontName="Courier",
                                textColor=colors.HexColor("#111133"),
                                backColor=colors.HexColor("#eef0f6"),
                                borderPadding=5, leftIndent=4, spaceAfter=6, spaceBefore=2)
    return st


def flow_diagram():
    """Boru hattinin dikey akis semasi."""
    steps = [
        ("1. Haftalık Tetik + Rotasyon", "Hafta numarasına göre 3 kategori + 3 semt seçilir"),
        ("2. Keşif — Overpass API", "Semtlerdeki işletmeler bulunur (ad, adres, telefon, site)"),
        ("3. Parmak İzi + Tekilleştirme", "isim|adres anahtarı; önceki haftalarda görülenler elenir"),
        ("4. Seçim (10 aday)", "Önce sitesi olmayanlar (~%60), sonra zayıf siteliler"),
        ("5. Web Sitesi Denetimi", "HTTPS, mobil, iletişim, randevu, hata kontrolleri"),
        ("6. Puanlama (Guardrails)", "YÜKSEK / ORTA / DÜŞÜK — nesnel kanıt şartıyla"),
        ("7. Kayıt — SQLite", "marco_leads tablosuna yazılır (gelecek haftalar için hafıza)"),
        ("8. PDF Raporu", "Parametreler → Bilgi & İletişim → Site sorunları"),
    ]
    box_w, box_h, gap = 150 * mm, 13 * mm, 6 * mm
    total_h = len(steps) * (box_h + gap) - gap
    d = Drawing(170 * mm, total_h)
    x = 10 * mm
    y = total_h - box_h
    for i, (title, desc) in enumerate(steps):
        d.add(Rect(x, y, box_w, box_h, rx=3, ry=3,
                   fillColor=NAVY if i % 2 == 0 else colors.HexColor("#2d2d52"),
                   strokeColor=None))
        d.add(String(x + 5 * mm, y + box_h - 5.2 * mm, title,
                     fontName=rpt.FONT_BOLD, fontSize=9.5, fillColor=colors.white))
        d.add(String(x + 5 * mm, y + 2.8 * mm, desc,
                     fontName=rpt.FONT, fontSize=8, fillColor=colors.HexColor("#c9c9dd")))
        if i < len(steps) - 1:
            cx = x + box_w / 2
            d.add(Line(cx, y, cx, y - gap + 1.8 * mm, strokeColor=NAVY, strokeWidth=1.4))
            d.add(Polygon([cx - 2 * mm, y - gap + 2.2 * mm, cx + 2 * mm, y - gap + 2.2 * mm,
                           cx, y - gap + 0.2 * mm], fillColor=NAVY, strokeColor=None))
        y -= box_h + gap
    return d


def two_col_table(rows, st, header=("Orijinal n8n düğümü", "LeadRadar karşılığı"), w1=70 * mm, w2=100 * mm):
    th = ParagraphStyle("th", fontSize=9.5, leading=13, fontName=rpt.FONT_BOLD, textColor=colors.white)
    data = [[Paragraph(header[0], th), Paragraph(header[1], th)]]
    for a, b in rows:
        data.append([Paragraph(a, st["cell"]), Paragraph(b, st["cell"])])
    t = Table(data, colWidths=[w1, w2], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build():
    st = styles()
    out_path = os.path.join(BASE_DIR, "docs", "LeadRadar_Sistem_Rehberi.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=20 * mm,
                            title="LeadRadar Sistem Rehberi")
    s = []
    P, H1, H2, LI, CODE = (lambda t: s.append(Paragraph(t, st["body"])),
                           lambda t: s.append(Paragraph(t, st["h1"])),
                           lambda t: s.append(Paragraph(t, st["h2"])),
                           lambda t: s.append(Paragraph("• " + t, st["li"])),
                           lambda t: s.append(Paragraph(t.replace(" ", "&nbsp;"), st["code"])))

    # ---------------- Kapak ----------------
    s.append(rpt._header_bar(
        "LeadRadar — Sistem Rehberi",
        f"Yerel İşletme Lead Keşif &amp; Zenginleştirme Sistemi • Uçtan uca çalışma mantığı • {datetime.now().strftime('%d.%m.%Y')}",
        st))
    s.append(Spacer(1, 6 * mm))
    P("Bu belge, n8n üzerindeki <b>\"Local Business Lead Discovery and Enrichment Agent\"</b> "
      "(Marco'nun Lead Avcısı) iş akışının n8n <b>kullanılmadan</b>, bağımsız bir Python yazılımı olarak "
      "yeniden inşa edilmiş hâli olan <b>LeadRadar</b>'in uçtan uca çalışma mantığını anlatır. "
      "Amaç: haftada bir çalışıp Berlin'deki küçük işletmelerden (kuaför, restoran, fitness salonu, diş hekimi) "
      "web sitesi olmayan ya da sorunlu olanları bulmak, kanıta dayalı biçimde puanlamak ve "
      "satış görüşmesine hazır bir PDF raporu üretmektir.")
    s.append(Spacer(1, 2 * mm))

    H1("1. Sistem Ne Yapar? (Kullanım Senaryosu)")
    P("Hedef kullanıcı, bir şehirde çalışan serbest web tasarımcısı / ajans sahibidir. Müşteri adayı bulmak için her hafta "
      "şu soruyu sorar: <i>\"Hangi yerel işletmelerin web sitesi yok ya da sitesi müşteri kaybettiriyor?\"</i> "
      "LeadRadar bu soruyu otomatik yanıtlar:")
    LI("Her hafta farklı kategori ve semt kombinasyonunu tarar (rotasyon).")
    LI("İşletmeleri; adı, adresi, telefonu ve web sitesi kaydıyla birlikte keşfeder.")
    LI("Önceki haftalarda bulunanları eler — her hafta <b>yeni</b> adaylar gelir.")
    LI("Sitesi olan adayların sitesini teknik olarak denetler (HTTPS, mobil uyum, iletişim yolları, bozuk linkler).")
    LI("Her adayı YÜKSEK / ORTA / DÜŞÜK fırsat skoruyla puanlar — yalnızca kanıtla.")
    LI("Sonuçları veritabanına kaydeder ve satışa hazır bir PDF raporu üretir.")

    H1("2. Uçtan Uca Akış Şeması")
    s.append(Spacer(1, 2 * mm))
    s.append(flow_diagram())
    s.append(PageBreak())

    # ---------------- Adim adim ----------------
    H1("3. Adım Adım Çalışma Mantığı")

    H2("Adım 1 — Haftalık Tetik ve Rotasyon (rotation.py)")
    P("Orijinal sistem her pazartesi 09:00'da tetiklenir. LeadRadar'de aynı işi <b>Windows Görev Zamanlayıcı</b> "
      "yapar (bkz. Bölüm 8) ya da <b>py run.py</b> komutuyla elle çalıştırılır. Yılın kaçıncı haftasında "
      "olduğumuz hesaplanır ve <b>hafta % 4</b> formülüyle 4 hazır rotasyondan biri seçilir. Böylece her hafta "
      "farklı 3 kategori + 3 semt taranır ve aynı işletmeler sürekli karşınıza çıkmaz. Rotasyon listeleri "
      "orijinal iş akışındaki 'Rotation Seed' düğümünün birebir aynısıdır.")
    CODE("Hafta 29 → kategoriler: Fitnessstudio, Zahnarzt, Friseur | semtler: Charlottenburg, Wilmersdorf, Schöneberg")

    H2("Adım 2 — Keşif (discover.py)")
    P("Orijinal akışta bir yapay zeka ajanı, Firecrawl'un <i>/search</i> ve <i>/scrape</i> araçlarıyla "
      "yelp.de ve gelbeseiten.de gibi rehberleri tarıyordu. LeadRadar bu adımı <b>OpenStreetMap Overpass API</b> "
      "ile yapar: ücretsizdir, API anahtarı gerektirmez ve işletme adı, adresi, telefonu ve "
      "<b>web sitesi kaydı</b> gibi yapısal veriyi doğrudan verir. Her semt için tek sorgu atılır; "
      "sonuçlar kategoriye eşlenir (ör. shop=hairdresser → Friseur). Kanıt linki olarak işletmenin "
      "OSM kaydı saklanır. OSM kaydında marka (brand) etiketi olan işletmeler ve bilinen zincir isimleri "
      "otomatik elenir — orijinaldeki 'zincir/franchise dışla' kuralı.")

    H2("Adım 3 — Parmak İzi ve Tekilleştirme (fingerprint.py + store.py)")
    P("Her aday için normalize edilmiş bir tekilleştirme anahtarı üretilir; öncelik sırası orijinaldekiyle aynıdır:")
    CODE("isim|adres  →  isim|telefon  →  isim|site-alan-adı  →  isim|")
    P("SQLite'taki <b>marco_leads</b> tablosunda saklanan tüm eski parmak izleri çekilir ve havuzdan "
      "daha önce görülen adaylar elenir. Bu, orijinal akıştaki 'Compute Fingerprint' + "
      "'Fetch Seen Fingerprints' + 'Filter Unseen (Top 10)' üçlüsünün karşılığıdır.")

    H2("Adım 4 — Seçim Önceliği")
    P("Orijinal ajan talimatı: <i>\"20 adayın en az 12'si web sitesi olmayan işletme olsun; kalanlar zayıf web "
      "varlığı olanlardan seçilsin.\"</i> LeadRadar aynı oranı korur: seçilen 10 adayın ~%60'ı web sitesi "
      "hiç olmayanlardan, kalanı önce 'yalnızca sosyal medya sayfası olanlar', sonra 'http:// (güvensiz) "
      "site kullananlar', en son normal siteli işletmelerden doldurulur. Kategori ve semt çeşitliliği "
      "korunur (round-robin).")

    H2("Adım 5 — Web Sitesi Denetimi (audit.py)")
    P("Orijinal akışta ikinci bir yapay zeka ajanı siteyi Firecrawl ile kazıyıp değerlendiriyordu. LeadRadar bu "
      "değerlendirmeyi <b>deterministik kodla</b> yapar — böylece sonuçlar tekrarlanabilir ve halüsinasyonsuzdur. "
      "Denetlenen <b>nesnel engeller</b> (objective blockers) orijinal guardrail listesinin birebir aynısıdır:")
    LI("<b>Site yüklenmiyor</b> — DNS/bağlantı hatası, HTTP 4xx/5xx, boş sayfa, sonsuz yönlendirme")
    LI("<b>HTTPS yok</b> — site şifrelenmemiş http üzerinden sunuluyor ya da SSL sertifikası geçersiz")
    LI("<b>Mobil uyumsuz</b> — sayfada viewport meta etiketi yok")
    LI("<b>İletişim yolu yok/bozuk</b> — telefon, e-posta, iletişim sayfası bulunamıyor ya da linki 404 veriyor")
    LI("<b>Randevu/rezervasyon yolu bozuk</b> — sitedeki randevu linki hata veriyor")
    P("Bunlara ek olarak <b>sezgisel</b> (heuristic) bulgular toplanır ve '[HEURISTIC]' önekiyle "
      "ayrı tutulur: eski telif yılı, çok eski jQuery/CMS sürümü, eksik SEO etiketleri vb. "
      "Ayrıca sitede bulunan telefonlar, e-postalar, sosyal medya linkleri ve teknoloji sinyalleri "
      "(WordPress, Wix, Jimdo...) çıkarılır — bunlar rapordaki iletişim planını besler.")

    H2("Adım 6 — Puanlama: Guardrail Kuralları (score.py)")
    P("Skorlama, orijinal sistem mesajındaki <b>'OPPORTUNITY SCORING — STRICT GUARDRAILS'</b> "
      "kurallarının koda dökülmüş hâlidir:")
    s.append(two_col_table([
        ("Web sitesi hiç yok (kaynakta site listelenmemiş)", "<b>YÜKSEK</b> — birebir hedef profil"),
        ("Resmî site yerine yalnızca Facebook/Instagram sayfası", "<b>YÜKSEK</b> — 'resmî site yok' sayılır (belgelenmiş ek karar)"),
        ("Site var + <b>en az 2</b> doğrulanmış nesnel engel", "<b>YÜKSEK</b>"),
        ("Site var + tam 1 nesnel engel", "<b>ORTA</b>"),
        ("Site var + 0 engel ama 2+ sezgisel bulgu", "<b>ORTA</b>"),
        ("HTTPS var + çalışan iletişim + bariz hata yok", "<b>ORTA veya DÜŞÜK</b> (asla YÜKSEK olamaz)"),
        ("Yalnızca sezgisel bulgular ('site eski görünüyor')", "Asla YÜKSEK üretemez — orijinal 3. kural"),
    ], st, header=("Durum", "Skor")))
    s.append(Spacer(1, 2 * mm))
    P("<b>why_lead</b> (neden aday?) alanı daima kanıta dayalıdır: ya rehber gerçeği ('site kaydı yok') "
      "ya da doğrulanmış 1-2 site sorunu yazılır. Sezgisel izlenimler bu alana değil, ayrı "
      "'sezgisel değerlendirme' bölümüne gider — orijinal 5. kural.")

    H2("Adım 7 — Kayıt (store.py)")
    P("Zenginleştirilen her aday SQLite'taki <b>marco_leads</b> tablosuna yazılır. Tablo şeması, orijinal "
      "iş akışındaki yapışkan notta verilen Postgres SQL'inin birebir SQLite karşılığıdır "
      "(+ 'district' ve 'emails' ek sütunları). Aynı parmak izi ikinci kez gelirse sessizce atlanır "
      "(INSERT OR IGNORE) — orijinaldeki continueOnFail davranışı. Bu tablo sistemin hafızasıdır: "
      "gelecek haftaların tekilleştirmesi buradan beslenir.")

    H2("Adım 8 — PDF Raporu (report.py)")
    P("Orijinal akış sonuçları HTML e-posta olarak Gmail ile gönderiyordu. LeadRadar bunun yerine "
      "<b>output/</b> klasörüne bir PDF raporu üretir. Rapor önce çalıştırma parametrelerini ve skora göre "
      "sıralı özet tabloyu (YÜKSEK → DÜŞÜK, orijinal e-postadaki sıralama) gösterir; ardından her aday için "
      "bir sayfa ayrılır ve şu sırayla sunulur:")
    LI("<b>1) Parametreler</b> — kategori, semt, skor, faaliyet durumu, güncellik ve teknoloji sinyalleri")
    LI("<b>2) Bilgiler ve İletişim</b> — adres, telefon, sitede bulunan e-postalar, sosyal medya, kanıt linki "
       "ve öncelik sıralı 'nasıl iletişime geçilir' planı + görüşme açılış önerisi")
    LI("<b>3) Web Sitesi Hata ve Sorunları</b> — doğrulanmış nesnel sorunlar, sezgisel bulgular ve "
       "teknik denetim ayrıntı tablosu")
    P("Ayrıca aynı klasöre, tüm ham verinin döküldüğü bir JSON dosyası yazılır (şeffaflık ve hata ayıklama için).")
    s.append(PageBreak())

    # ---------------- Esleme tablosu ----------------
    H1("4. Orijinal n8n Düğümleri ↔ LeadRadar Modülleri")
    s.append(two_col_table([
        ("Schedule Trigger (Pzt 09:00 cron)", "Windows Görev Zamanlayıcı / elle <b>py run.py</b>"),
        ("Rotation Seed (Code)", "leadradar/rotation.py — aynı hafta formülü, aynı listeler"),
        ("AI Agent — Discover Fresh (GPT-5.1)", "leadradar/discover.py — Overpass API ile deterministik keşif"),
        ("/search + /scrape in Firecrawl (araçlar)", "Overpass (temel keşif) + <b>Firecrawl</b> "
         "(açıksa: rehberlerden puan/yorum + JS'li site tarama) — leadradar/firecrawl_client.py"),
        ("Parse Refill Output (Code)", "discover.py içindeki alan eşleme (element_to_lead)"),
        ("Compute Fingerprint (Code)", "leadradar/fingerprint.py — aynı normalizasyon ve öncelik"),
        ("Fetch Seen Fingerprints (Postgres)", "leadradar/store.py — SQLite SELECT fingerprint"),
        ("Filter Unseen Top 10 (Code)", "run.py — havuzdan yeni olanları seçme + select_final"),
        ("Enrich Prep / Parse (Code)", "run.py döngüsü + score.py alan üretimi"),
        ("AI Agent — enrichment (GPT-5.1)", "leadradar/audit.py + score.py — kural tabanlı denetim ve guardrail puanlama"),
        ("Postgres — Insert Lead", "store.py insert_lead (INSERT OR IGNORE)"),
        ("Aggregate + Build Email HTML", "leadradar/report.py — PDF üretimi"),
        ("Gmail — Send Weekly Summary", "output/LeadRadar_Lead_Raporu_&lt;tarih&gt;.pdf dosyası"),
    ], st))
    s.append(Spacer(1, 3 * mm))
    P("<b>Neden yapay zeka ajanları yerine kural tabanlı kod?</b> Orijinaldeki guardrail talimatlarının "
      "neredeyse tamamı zaten nesnel, kodla doğrulanabilir kontrollerdi (HTTPS var mı, viewport var mı, "
      "iletişim linki çalışıyor mu...). Kod bu kontrolleri halüsinasyon riski olmadan, API maliyeti "
      "olmadan ve her seferinde aynı sonuçla yapar. İsteğe bağlı yapay zeka cilası (Bölüm 7) yine de mevcuttur.")
    s.append(Spacer(1, 2 * mm))
    P("<b>Firecrawl entegrasyonu (isteğe bağlı, config.json → firecrawl.enabled).</b> Orijinal akıştaki "
      "Firecrawl araçları bu sistemde de kullanılabilir. Açıkken iki ek yetenek devreye girer: "
      "(1) her aday için yelp.de / gelbeseiten.de / jameda.de gibi rehberler taranarak <b>puan ve yorum sayısı</b> "
      "doldurulur (OSM bu veriyi tutmaz); (2) yerel tarayıcı ince/boş içerik gördüğünde "
      "(JavaScript ile yüklenen siteler) site <b>Firecrawl ile yeniden taranır</b> ve gerçek içerik denetlenir. "
      "Anahtar önce FIRECRAWL_API_KEY ortam değişkeninde, yoksa Firecrawl CLI'nin kaydettiği dosyada aranır — "
      "yani firecrawl CLI ile giriş yaptıysanız ek ayar gerekmez. Firecrawl kapalıyken sistem tamamen "
      "ücretsiz ve eskisi gibi çalışır; skorlar her iki durumda da kural tabanlıdır.")

    H1("5. Veritabanı Şeması (data/leads.db)")
    CODE("CREATE TABLE marco_leads (")
    CODE("  id INTEGER PRIMARY KEY, fingerprint TEXT UNIQUE,")
    CODE("  business_name TEXT NOT NULL, category TEXT, address TEXT,")
    CODE("  phone TEXT, website TEXT, public_rating TEXT, review_count TEXT,")
    CODE("  website_issues TEXT, heuristic_assessment TEXT, services_listed TEXT,")
    CODE("  tech_signals TEXT, freshness_signal TEXT, operating_status TEXT,")
    CODE("  opportunity_score TEXT, why_lead TEXT, source_links TEXT,")
    CODE("  week_of TEXT, discovered_at TEXT, district TEXT, emails TEXT )")
    P("Veriyi incelemek için herhangi bir SQLite aracı (ör. DB Browser for SQLite) kullanılabilir.")

    H1("6. Kurulum ve Çalıştırma")
    LI("Gereksinim: Python 3.10+ (bu makinede 3.14 kurulu) ve internet bağlantısı.")
    CODE("py -m pip install -r requirements.txt")
    CODE("cd C:\\Users\\furka\\Music\\LeadRadar")
    CODE("py run.py                # tam haftalık çalıştırma")
    CODE("py run.py --limit 5      # daha az adayla hızlı deneme")
    CODE("py run.py --week 31      # başka bir rotasyon haftasını zorla")
    P("Çıktılar: <b>output/LeadRadar_Lead_Raporu_&lt;tarih&gt;.pdf</b> (rapor), "
      "<b>output/LeadRadar_calistirma_&lt;tarih&gt;.json</b> (ham veri), <b>data/leads.db</b> (hafıza).")

    H1("7. Yapılandırma (config.json)")
    s.append(two_col_table([
        ("city", "Hedef şehir (varsayılan: Berlin). Overpass sayesinde başka şehirler de çalışır; "
                 "semtler için area_rotation ve idari seviyeler için *_admin_levels ayarlanmalıdır."),
        ("target_leads / discover_pool", "Rapora seçilecek aday sayısı (10) / keşif havuzu (20) — orijinal oranlar."),
        ("no_website_ratio", "Seçimde 'web sitesi yok' kotası (0.6 = %60)."),
        ("category_rotation / area_rotation", "Haftalık rotasyon listeleri — orijinalle birebir aynı."),
        ("category_osm", "Kategori → OSM etiket eşlemesi. Yeni kategori eklemek için buraya satır eklenir."),
        ("chain_blacklist", "Zincir/franchise isim filtresi (brand etiketi olanlar zaten otomatik elenir)."),
        ("request_delay_sec / http_timeout", "Nazik tarama: istekler arası bekleme ve zaman aşımı."),
        ("firecrawl.enabled", "İsteğe bağlı Firecrawl zenginleştirmesi (puan/yorum + JS'li site tarama)."),
        ("firecrawl.enrich_ratings / scrape_sites", "Sırasıyla: rehberden puan çekme / ince siteleri Firecrawl ile tarama."),
        ("ai.enabled / ai.provider", "İsteğe bağlı yapay zeka cilası (Bölüm 7.1)."),
    ], st, header=("Ayar", "Açıklama")))
    s.append(Spacer(1, 2 * mm))

    H2("7.1 İsteğe bağlı yapay zeka cilası (ai_polish.py)")
    P("Orijinal akıştaki gibi metinlerin bir dil modeliyle zenginleştirilmesini isterseniz: "
      "config.json içinde <b>\"ai\": {\"enabled\": true}</b> yapın ve ortam değişkeni olarak "
      "<b>ANTHROPIC_API_KEY</b> (veya provider=openai için OPENAI_API_KEY) tanımlayın. Bu durumda "
      "her adayın 'neden aday?' gerekçesi ve sezgisel değerlendirmesi, denetim kanıtlarına dayanarak "
      "dil modeli tarafından yeniden yazılır. Kapalıyken sistem tamamen ücretsiz ve çevrimdışı "
      "puanlama mantığıyla çalışır; skorlar her iki durumda da kural tabanlıdır (model skoru değiştiremez).")

    H1("8. Haftalık Otomatik Çalıştırma (Pazartesi 09:00)")
    P("Orijinal akıştaki cron tetikleyicisinin (0 9 * * 1) Windows karşılığını kurmak için proje "
      "klasöründeki hazır betiği <b>bir kez</b> çalıştırın:")
    CODE("powershell -ExecutionPolicy Bypass -File haftalik_zamanlama.ps1")
    P("Betik, Görev Zamanlayıcı'da her pazartesi 09:00'da <b>py run.py</b> komutunu çalıştıran "
      "'LeadRadar Lead Avcisi' adlı görevi oluşturur. Kaldırmak için: "
      "<b>schtasks /Delete /TN \"LeadRadar Lead Avcisi\" /F</b>")

    H1("9. Orijinalden Farklar ve Sınırlar (Dürüst Liste)")
    s.append(two_col_table([
        ("Firecrawl + GPT-5.1 keşfi", "Overpass API (ücretsiz, anahtarsız). Yelp/GelbeSeiten puanları "
         "alınamadığı için public_rating / review_count alanları boş kalır."),
        ("'Rehberde site yok' kanıtı", "OSM kaydında site alanının boş olması kanıt sayılır. OSM eksik "
         "olabilir; işletmenin aslında sitesi olabilir — aramadan önce hızlı bir Google kontrolü önerilir."),
        ("Yapay zeka değerlendirmesi", "Kural tabanlı denetim + isteğe bağlı yapay zeka cilası. "
         "Skorlar deterministiktir, tekrarlanabilir."),
        ("Postgres (Supabase)", "SQLite — kurulum gerektirmez, tek dosya (data/leads.db)."),
        ("Gmail e-postası", "PDF raporu (output/ klasörü)."),
        ("Faaliyet durumu (yorum tazeliği)", "Yorum verisi olmadığından telefon/çalışma saati/site erişimi "
         "gibi dolaylı sinyallerle tahmin edilir ve raporda 'teyit önerilir' diye işaretlenir."),
    ], st, header=("Orijinal", "LeadRadar yaklaşımı")))
    s.append(Spacer(1, 2 * mm))
    P("<b>Etik not:</b> Sistem yalnızca halka açık işletme bilgilerini kullanır, sitelere saniyeler arayla "
      "tek tek istek atar (nazik tarama) ve hiçbir yere otomatik mesaj göndermez — iletişim kararı her "
      "zaman size aittir.")

    H1("10. Sık Sorulanlar / Sorun Giderme")
    LI("<b>Rapor boş geldi:</b> O haftanın semtlerinde yeni aday kalmamış olabilir. --week ile başka "
       "rotasyon deneyin ya da data/leads.db dosyasını silerek hafızayı sıfırlayın.")
    LI("<b>Overpass hatası (429/504):</b> Sunucu yoğun; sistem otomatik bekleyip yedek uca geçer. "
       "Sorun sürerse birkaç dakika sonra tekrar çalıştırın.")
    LI("<b>Türkçe karakterler bozuk görünüyor:</b> PDF'te görünmez (gömülü Segoe UI/Arial kullanılır); "
       "yalnızca konsol çıktısında görülebilir, zararsızdır.")
    LI("<b>Başka şehir istiyorum:</b> config.json'da city + area_rotation değerlerini değiştirin "
       "(ör. city=İstanbul, semtler=Kadıköy, Beşiktaş...; city_admin_levels için Türkiye'de '4', "
       "district_admin_levels için '6|8' iyi bir başlangıçtır).")
    LI("<b>Aday sayısını artırmak:</b> config.json'da target_leads ve discover_pool değerlerini yükseltin.")

    doc.build(s, onFirstPage=rpt._footer, onLaterPages=rpt._footer)
    print(f"Rehber hazır: {out_path}")
    return out_path


if __name__ == "__main__":
    build()
