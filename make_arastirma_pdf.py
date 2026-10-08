# -*- coding: utf-8 -*-
# LeadRadar — yerel işletme lead keşif ve zenginleştirme sistemi
# Copyright (c) 2026 Furkan Akduman · https://github.com/FlyerFukas
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
#
# Ticari olmayan kullanım serbesttir (bkz. LICENSE).
# İşletmeler ve her türlü ticari kullanım ayrı, ücretli lisans gerektirir.
# Ayrıntı ve iletişim: COMMERCIAL.md
"""LeadRadar — Araştırma Çerçevesi ve Literatür Haritası (PDF üretici).

Akademik danışmana yönelik üst düzey belge: sistem genel olarak ne yapıyor,
benzer sistemlerden farkı nedir, ürettiği veri ambarıyla hangi araştırma
soruları sorulabilir ve literatür taraması hangi başlıklardan yürütülmelidir.

Kullanim:  py make_arastirma_pdf.py
Cikti:     docs/LeadRadar_Arastirma_Cercevesi.pdf
"""

import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from leadradar import report as rpt
from leadradar.config import load_config

NAVY = rpt.NAVY
GRID = rpt.GRID
LIGHT = rpt.LIGHT
CFG = load_config(os.path.join(BASE_DIR, "config.json"))


def styles():
    rpt._register_fonts()
    st = rpt._styles()
    st["h1"] = ParagraphStyle("ah1", fontSize=15.5, leading=20, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=11, spaceAfter=7)
    st["h2"] = ParagraphStyle("ah2", fontSize=12, leading=16, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=9, spaceAfter=4)
    st["h3"] = ParagraphStyle("ah3", fontSize=10.5, leading=14, fontName=rpt.FONT_BOLD,
                              textColor=colors.HexColor("#3a4263"), spaceBefore=7, spaceAfter=3)
    st["body"] = ParagraphStyle("ab", fontSize=9.8, leading=14.2, fontName=rpt.FONT,
                                textColor=colors.HexColor("#222230"), spaceAfter=5, alignment=4)
    st["li"] = ParagraphStyle("ali", parent=st["body"], leftIndent=6 * mm, spaceAfter=2.5)
    st["li2"] = ParagraphStyle("ali2", parent=st["body"], leftIndent=12 * mm, spaceAfter=2,
                               fontSize=9.4, leading=13)
    st["note"] = ParagraphStyle("an", fontSize=9.2, leading=13, fontName=rpt.FONT,
                                textColor=colors.HexColor("#4a5164"), leftIndent=5 * mm,
                                rightIndent=4 * mm, spaceBefore=4, spaceAfter=6,
                                borderPadding=6, backColor=colors.HexColor("#eef1f8"))
    st["big"] = ParagraphStyle("abig", fontSize=11, leading=16, fontName=rpt.FONT,
                               textColor=colors.HexColor("#1a1a2e"), spaceAfter=6,
                               leftIndent=4 * mm, rightIndent=4 * mm, borderPadding=8,
                               backColor=colors.HexColor("#f3f5fb"), alignment=4)
    return st


def table(rows, st, header, widths, small=False):
    th = ParagraphStyle("th", fontSize=8.8, leading=11.5, fontName=rpt.FONT_BOLD, textColor=colors.white)
    cs = ParagraphStyle("cs", parent=st["cell"], fontSize=8.6 if small else 9, leading=11.8 if small else 12.5)
    data = [[Paragraph(h, th) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), cs) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t


def build():
    st = styles()
    out = os.path.join(BASE_DIR, "docs", "LeadRadar_Arastirma_Cercevesi.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=16 * mm, bottomMargin=20 * mm,
                            title="LeadRadar — Araştırma Çerçevesi ve Literatür Haritası",
                            author="Furkan Akduman")
    s = []
    P = lambda t: s.append(Paragraph(t, st["body"]))
    H1 = lambda t: s.append(Paragraph(t, st["h1"]))
    H2 = lambda t: s.append(Paragraph(t, st["h2"]))
    H3 = lambda t: s.append(Paragraph(t, st["h3"]))
    LI = lambda t: s.append(Paragraph("• " + t, st["li"]))
    L2 = lambda t: s.append(Paragraph("– " + t, st["li2"]))
    NOTE = lambda t: s.append(Paragraph(t, st["note"]))
    BIG = lambda t: s.append(Paragraph(t, st["big"]))
    GAP = lambda h=3: s.append(Spacer(1, h * mm))

    nsehir = len(CFG["city_catalog"])
    nsektor = len(CFG["category_osm"])

    # ---------- Kapak ----------
    s.append(rpt._header_bar(
        "LeadRadar — Araştırma Çerçevesi",
        f"Genel konumlandırma, veri ambarı ve literatür haritası "
        f"&nbsp;•&nbsp; {datetime.now().strftime('%d.%m.%Y')}", st))
    GAP(5)
    P("Bu belge, eşlik eden <b>Teorik Çerçeve ve Yöntem</b> belgesinin üst düzey "
      "tamamlayıcısıdır. Diğer belge sistemin iç işleyişini ayrıntılandırır; bu belge "
      "üç soruya cevap verir: <b>(1)</b> sistem genel olarak ne yapmaktadır ve benzer "
      "uygulamalardan nasıl ayrışır, <b>(2)</b> ürettiği veri ambarı hangi araştırma "
      "sorularına açıktır, <b>(3)</b> literatür taraması hangi ana başlıklardan "
      "yürütülmelidir.")

    # ---------- 1 ----------
    H1("1. Sistem genel olarak ne yapıyor")
    BIG("Sistem, açık coğrafi veriden bir bölgedeki işletmelerin listesini çıkarır, her "
        "işletmenin <b>internet üzerindeki varlığını fiilen gözlemler</b> ve bu varlığın "
        "eksikliğini ölçülebilir göstergelere dayanarak derecelendirir. Kısaca: "
        "<b>haritadan işletme çıkarır, web'den o işletmenin dijital varlığını ölçer, "
        "ikisini birleştirip sıralar.</b>")
    GAP(2)
    P("Üç cümlelik özet, farklı soyutlama düzeylerinde:")
    LI("<b>Teknik:</b> Açık coğrafi veri tabanından mekânsal sorguyla çekilen işletme "
       "kayıtları, canlı web gözlemiyle zenginleştirilir ve kural tabanlı bir "
       "sınıflandırıcıyla önceliklendirilir.")
    LI("<b>Akademik:</b> Firma düzeyinde dijital varlık, ikincil açık veri ile doğrudan "
       "web ölçümü birleştirilerek, yeniden üretilebilir bir boru hattında ölçülür.")
    LI("<b>Pratik:</b> Bir şehirdeki hangi işletmelerin web sitesi yok ya da sitesi "
       "çalışmıyor, bu sorulara otomatik ve belgelenebilir bir yanıt üretir.")
    GAP(1)
    P("Analiz birimi <b>işletmedir</b>, kullanıcı değil. Ölçülen şey bir <b>yokluk ya da "
      "kusurdur</b>, bir tercih ya da memnuniyet değil. Bu iki nokta, sistemi gündelik "
      "konum tabanlı uygulamalardan ayıran temel farktır.")

    # ---------- 2 ----------
    H1("2. Benzer sistemlerden farkı")
    P("Soru sıklıkla şöyle geliyor: \"Yemeksepeti ya da Google Haritalar da işletmeleri "
      "haritadan buluyor, farkı ne?\" Fark, veride değil <b>sorunun yönündedir</b>.")
    GAP(1)
    s.append(table([
        ["Yemeksepeti, Getir, Trendyol Yemek",
         "Kullanıcıyı en yakın hizmete bağlar",
         "\"Bana en yakın X nerede?\"",
         "Kendi anlaşmalı işletme ağı (kapalı)",
         "Talep tarafı, işlem odaklı"],
        ["Google Haritalar / Places",
         "Mekân arama, yol tarifi, bilgi kartı",
         "\"X nerede, nasıl giderim?\"",
         "Tescilli, kapalı veri tabanı",
         "Talep tarafı, erişim odaklı"],
        ["Yelp, TripAdvisor",
         "Değerlendirme ve sıralama",
         "\"X iyi mi?\"",
         "Kullanıcı yorumları",
         "Talep tarafı, kalite sinyali"],
        ["<b>LeadRadar</b>",
         "<b>İşletmenin dijital varlığını denetler, eksikliğe göre sıralar</b>",
         "<b>\"Hangi işletmenin dijital varlığı eksik?\"</b>",
         "<b>Açık veri (OSM) + canlı web gözlemi</b>",
         "<b>Arz tarafı, eksiklik odaklı</b>"],
    ], st, ["Sistem", "İşlevi", "Yanıtladığı soru", "Veri kaynağı", "Konumu"],
        [34 * mm, 38 * mm, 36 * mm, 32 * mm, 30 * mm], small=True))
    GAP(2)
    P("İki ayrım özellikle vurgulanmalıdır.")
    H3("2.1 Talep tarafı ile arz tarafı ayrımı")
    P("Sayılan uygulamalar <b>talep tarafı</b> sistemlerdir: bir tüketiciyi bir işletmeye "
      "bağlamayı amaçlar, başarı ölçütü eşleşmenin hızı ve isabetidir. LeadRadar ise "
      "<b>arz tarafı</b> bir sistemdir: analiz birimi işletmenin kendisidir ve amaç bir "
      "eşleşme değil, işletme popülasyonu üzerinde bir <b>niteliğin ölçülmesidir</b>. "
      "Bu nedenle çıktısı bir arama sonucu değil, bir denetim raporudur.")
    H3("2.2 Varlığı değil yokluğu ölçmek")
    P("Konum tabanlı uygulamalar var olanı listeler: açık olan restoranlar, puanı yüksek "
      "kuaförler. LeadRadar <b>olmayanı</b> tespit etmeye çalışır: web sitesi bulunmayan "
      "ya da sitesi işlevsiz olan işletmeler. Yokluğun ölçülmesi metodolojik olarak farklı "
      "bir problemdir; çünkü \"kayıtta yok\" ile \"gerçekte yok\" aynı şey değildir. "
      "Bu ayrım eşlik eden yöntem belgesinin 6. bölümünde ayrıntılı tartışılmaktadır.")
    NOTE("<b>Konumlandırma cümlesi.</b> Sistem bir arama ya da teslimat uygulaması değil, "
         "<b>işletme popülasyonu üzerinde çalışan bir dijital varlık denetim aracıdır</b>. "
         "En yakın akrabası, konum tabanlı tüketici uygulamaları değil, pazar araştırması "
         "ve firma düzeyinde dijitalleşme ölçümü yapan çalışmalardır.")

    # ---------- 3 ----------
    H1("3. Üretilen veri ambarı")
    P("Her çalıştırma, raporun yanında <b>taranan ham verinin tamamını</b> ayrı dosyalar "
      "halinde üretir. Bu, sistemin asıl araştırma değerinin bulunduğu yerdir: satışa "
      "yönelik rapor yalnızca küçük bir alt kümedir.")
    GAP(1)
    s.append(table([
        ["<b>Taranan veri (CSV)</b>", "Taranan her OSM kaydı, koordinatıyla ve boru hattındaki akıbetiyle",
         "Excel ile doğrudan açılır, istatistik yazılımına aktarılır"],
        ["<b>Taranan veri (JSON)</b>", "Aynı kayıtlar, ham OSM etiketlerinin tamamıyla",
         "Etiket düzeyinde analiz, yeniden işleme"],
        ["Çalıştırma dökümü (JSON)", "Rapora giren adayların denetim ayrıntısı",
         "Web ölçüm sonuçlarının incelenmesi"],
        ["Lead raporu (PDF)", "Seçilmiş adaylar, insan okuması için", "Uygulama çıktısı"],
    ], st, ["Dosya", "İçerik", "Kullanım"], [38 * mm, 66 * mm, 66 * mm]))
    GAP(2)
    H2("3.1 Kayıt başına tutulan alanlar")
    P("Ham veri dosyasında her satır bir OSM kaydıdır ve şunları içerir:")
    LI("<b>Mekânsal:</b> enlem, boylam, OSM nesne türü ve kimliği, arama bölgesi")
    LI("<b>Kimlik:</b> işletme adı, adres bileşenleri, telefon")
    LI("<b>Sınıflandırma:</b> atanan sektör kategorisi, ham OSM etiketlerinin tamamı, etiket sayısı")
    LI("<b>Dijital varlık:</b> web adresi, varlık durumu (yok / yalnızca sosyal medya / güvensiz / var)")
    LI("<b>Zaman:</b> OSM kontrol tarihi, açılış saatleri")
    LI("<b>Akıbet:</b> kaydın hangi aşamada elendiği ya da rapora seçildiği, eleme sebebi")
    GAP(1)
    P("Son madde yöntemsel olarak önemlidir. Elenen kayıtlar silinmez, <b>sebebiyle "
      "birlikte saklanır</b>. Böylece her çalıştırma için bir <b>eleme akış tablosu</b> "
      "(<i>attrition table</i>) kurulabilir ve çerçevenin nasıl daraldığı sayısal olarak "
      "gösterilebilir.")
    GAP(1)
    P("Gerçek bir çalıştırmadan örnek (Bonn, kuaför sektörü, tüm şehir taraması):")
    GAP(1)
    s.append(table([
        ["Ham OSM kaydı (Overpass yanıtı)", "200", "Çerçevenin başlangıç büyüklüğü"],
        ["Zincir markası olduğu için elenen", "2", "<i>brand</i> etiketi taşıyan kayıtlar"],
        ["Aynı taramada mükerrer", "2", "Parmak izi çakışması"],
        ["Çerçeveye giren", "196", "Analiz edilebilir kayıt"],
        ["Öncelik havuzuna alınan", "20", "Kota ve çeşitlilik kuralıyla"],
        ["Rapora seçilen", "3", "Bu çalıştırmada istenen aday sayısı"],
    ], st, ["Aşama", "Kayıt", "Açıklama"], [60 * mm, 22 * mm, 88 * mm]))
    NOTE("Rapora giren 3 kayıt ile elimizde tutulan 200 kayıt arasındaki fark, bu projenin "
         "akademik potansiyelinin bulunduğu yerdir. Ticari çıktı 3 satırdır; "
         "<b>araştırma verisi 200 satırdır</b> ve her hafta, her şehir, her sektör için "
         "yeniden üretilebilir.")

    # ---------- 4 ----------
    H1("4. Bu veriyle hangi sorular sorulabilir")
    P("Aşağıdaki sorular mevcut sistemle, ek bir altyapı kurmadan veri üretilerek "
      "çalışılabilir. Her başlık ayrı bir çalışma konusudur.")

    H2("4.1 Mekânsal desenler")
    LI("Dijital varlık eksikliği mekânsal olarak <b>kümeleniyor mu?</b> Sitesi olmayan "
       "işletmeler belirli mahallelerde yoğunlaşıyor mu, yoksa rastgele mi dağılıyor? "
       "(mekânsal otokorelasyon, sıcak nokta analizi)")
    LI("Merkez ile çeper arasında fark var mı? Şehir merkezine uzaklık ile dijital varlık "
       "arasında bir ilişki kurulabilir mi?")
    LI("<b>Komşuluk etkisi</b> var mı? Çevresindeki işletmelerin siteye sahip olması, bir "
       "işletmenin siteye sahip olma olasılığını artırıyor mu?")
    LI("Mahalle düzeyi sosyoekonomik göstergelerle (gelir, kira, eğitim, yaş yapısı) "
       "ilişkilendirilebilir mi?")

    H2("4.2 Sektörel ve ekonomik desenler")
    LI("Sektörler arasında dijitalleşme farkı ne kadar? Hangi sektörler geride?")
    LI("Zincir işletmeler ile bağımsız işletmeler arasındaki fark ölçülebilir mi? "
       "(sistem zincirleri etiketleyerek eliyor, yani ikisi ayrı ayrı ölçülebilir)")
    LI("Şehir büyüklüğü ile dijitalleşme arasında ilişki var mı? Katalogdaki "
       f"{nsehir} şehir bu karşılaştırmaya imkân verir.")
    LI("İşletmenin yaşı, büyüklüğü ya da türü (sağlık, yeme-içme, perakende) ile dijital "
       "varlık arasında sistematik bir fark var mı?")

    H2("4.3 Zaman boyutu (panel kurulumu)")
    LI("Aynı bölge altı ay arayla tarandığında ne değişiyor? <b>Dijitalleşme hızı</b> "
       "ölçülebilir hale gelir.")
    LI("Site açan işletmelerin profili nedir? Hangi özellikler siteye geçişi öngörüyor?")
    LI("Kapanan işletmeler tespit edilebilir mi? (OSM kaydı duruyor ama site ve telefon ölü)")
    NOTE("Sistem şu anda her çalıştırmayı tarih damgalı ayrı dosyalara yazdığı için, "
         "<b>panel veri seti zaten birikmektedir</b>. Bugün başlanan düzenli taramalar, "
         "bir yıl sonra zaman serisi analizine imkân verir. Bu, erken başlamanın "
         "değerli olduğu bir tasarım özelliğidir.")

    H2("4.4 Veri kalitesi ve gönüllü coğrafi bilgi")
    LI("OSM'nin firma kapsamı ne kadar? Resmî sicil kayıtlarıyla eşleştirilerek "
       "kapsama oranı sektör ve bölge bazında kestirilebilir mi?")
    LI("OSM kayıtlarındaki eksiklik rastgele mi, yoksa işletme özellikleriyle ilişkili mi?")
    LI("Etiket zenginliği (kayıt başına etiket sayısı) ile kayıt doğruluğu arasında "
       "ilişki var mı? Sistem bu alanı zaten tutmaktadır.")

    H2("4.5 Politika ve kalkınma")
    LI("KOBİ dijitalleşme destek programları <b>nereye hedeflenmeli?</b> Sistem, desteğe "
       "en çok ihtiyaç duyan bölge ve sektörleri veriyle gösterebilir.")
    LI("Firma düzeyinde <b>dijital uçurum</b> ölçülebilir mi? Literatürde dijital uçurum "
       "çoğunlukla bireyler üzerinden ölçülür; işletme tarafı görece az çalışılmıştır.")
    LI("Aynı yöntem Türkiye'ye uygulanırsa ne çıkar? Karşılaştırmalı bir çalışma mümkün mü?")

    H2("4.6 Yöntem araştırması")
    LI("Aynı görevi dil modeli ajanlarıyla çözen bir sistem ile kural tabanlı deterministik "
       "bir hat, <b>tutarlılık, doğruluk ve maliyet</b> açısından nasıl karşılaştırılır? "
       "Projenin kökeninde bu karşılaştırma fiilen yapılmıştır.")
    LI("Kayıt eşleştirmede deterministik hiyerarşik anahtarın başarımı, olasılıksal "
       "yöntemlere göre ne durumda?")

    # ---------- 5 ----------
    H1("5. Literatür taraması için başlık haritası")
    P("Aşağıdaki yapı, taramanın yürütüleceği <b>ana alanları</b> ve her alanın altındaki "
      "<b>aranabilir anahtar terimleri</b> verir. Türkçe karşılıklar yanlarında "
      "belirtilmiştir; uluslararası literatürde İngilizce terimlerle arama yapılması "
      "önerilir.")

    H2("A. Coğrafi Bilgi Sistemleri ve Mekânsal Veri Bilimi")
    P("<i>Projenin veri kaynağı tarafının ana alanı. Haritadan veri çıkarma işinin "
      "kuramsal zemini buradadır.</i>")
    L2("Volunteered Geographic Information (VGI) / gönüllü coğrafi bilgi")
    L2("OpenStreetMap data quality, completeness, coverage assessment")
    L2("Spatial data mining / mekânsal veri madenciliği")
    L2("Point of Interest (POI) data analysis / ilgi noktası verisi")
    L2("Geospatial data extraction, Overpass API, spatial query")
    L2("Crowdsourced geographic data / kitle kaynaklı coğrafi veri")

    H2("B. İşletme Dijitalleşmesi ve Dijital Uçurum")
    P("<i>Ölçülen olgunun ana alanı. Bulguların anlamlandırılacağı literatür burasıdır.</i>")
    L2("SME digitalization / KOBİ dijitalleşmesi")
    L2("Firm-level digital divide / firma düzeyinde dijital uçurum")
    L2("Digital maturity assessment / dijital olgunluk ölçümü")
    L2("Web presence of small businesses / küçük işletmelerde web varlığı")
    L2("Technology adoption: TAM, TOE framework, diffusion of innovations")
    L2("Digital transformation in local services / yerel hizmetlerde dijital dönüşüm")

    H2("C. Web Ölçümü ve Otomatik Site Değerlendirme")
    P("<i>Öznitelik çıkarımı tarafının ana alanı. Siteyi nasıl ölçtüğümüzün literatürü.</i>")
    L2("Web measurement / web observatory / large-scale web crawling")
    L2("Automated website quality assessment / otomatik site kalite değerlendirmesi")
    L2("Web accessibility auditing, WCAG automated evaluation")
    L2("Mobile-friendliness assessment, responsive design detection")
    L2("Digital footprint analysis / dijital ayak izi")
    L2("HTTPS adoption measurement / güvenli aktarım yaygınlığı ölçümü")

    H2("D. Kayıt Eşleştirme ve Veri Bütünleştirme")
    P("<i>Tekilleştirme tarafının ana alanı.</i>")
    L2("Record linkage / entity resolution / kayıt eşleştirme")
    L2("Deterministic versus probabilistic matching, Fellegi-Sunter model")
    L2("Data fusion, data integration from heterogeneous sources")
    L2("Deduplication in administrative data / idari veride tekilleştirme")

    H2("E. Örnekleme, Veri Kalitesi ve Alternatif Veri Kaynakları")
    P("<i>İstatistik bölümünün en doğrudan katkı yapabileceği alan.</i>")
    L2("Total Survey Error framework / toplam anket hatası çerçevesi")
    L2("Coverage error, frame error, undercoverage in non-probability samples")
    L2("Non-probability sampling, purposive sampling and inference limits")
    L2("Missing data mechanisms: MCAR, MAR, MNAR")
    L2("Big data and official statistics / alternatif veri kaynaklarının resmî istatistikte kullanımı")
    L2("Digital trace data / dijital iz verisi ve temsil sorunu")

    H2("F. Yapay Zekâ Destekli Sistem Tasarımı")
    P("<i>Projenin mimari tercihini savunacağı alan: neden kural tabanlı, neden LLM değil.</i>")
    L2("Rule-based systems versus machine learning / kural tabanlı sistemler")
    L2("Explainable AI (XAI), interpretability in decision support")
    L2("LLM agents in production pipelines, agentic workflows, reliability")
    L2("Human-in-the-loop decision support systems")
    L2("Reproducibility in computational research / hesaplamalı araştırmada yeniden üretilebilirlik")
    L2("Determinism versus stochasticity in automated pipelines")

    H2("G. Uygulama Alanı: Pazar İstihbaratı")
    P("<i>Ticari tarafın literatürü. Makalenin uygulama bölümü için.</i>")
    L2("B2B lead generation and lead scoring / müşteri adayı puanlama")
    L2("Sales intelligence, market intelligence systems")
    L2("Prospect prioritization models")
    L2("Local business marketing, hyperlocal targeting")

    NOTE("<b>Taramaya nereden başlanmalı.</b> Projenin özgün kesişimi <b>A ile B</b> "
         "arasındadır: açık coğrafi veriyle firma düzeyinde dijitalleşme ölçümü. "
         "C alanı yöntemi, E alanı ise geçerlilik tartışmasını besler. Tarama bu "
         "sırayla yürütülürse, projenin literatürdeki boşluğu daha net görünür.")

    # ---------- 6 ----------
    H1("6. Olası makale çerçeveleri")
    P("Aynı çalışma farklı eksenlerden yazılabilir. Aşağıdaki dört çerçeve, vurgunun "
      "nereye konulacağına göre ayrışır. Danışmanın hangisini seçeceği, hedeflenen "
      "derginin alanına bağlıdır.")
    GAP(1)
    s.append(table([
        ["<b>1. Yöntem makalesi</b>",
         "Açık coğrafi veri ile firma düzeyinde dijital varlık ölçümü: yeniden üretilebilir bir boru hattı",
         "A + E + F", "Yöntemin kendisi katkıdır; bulgular örnekleyicidir"],
        ["<b>2. Ampirik makale</b>",
         "Yerel hizmet sektöründe dijital varlık eksikliği: mekânsal ve sektörel desenler",
         "A + B", "Veri toplanmalı; birden çok şehir ve sektör gerekir"],
        ["<b>3. Karşılaştırmalı yöntem</b>",
         "Dil modeli ajanları ile kural tabanlı hatların uygulamalı karşılaştırması",
         "F", "Her iki sistem de mevcut; ölçüm tasarımı kurulmalı"],
        ["<b>4. Veri kalitesi</b>",
         "Gönüllü coğrafi bilgide firma kapsamı ve eksikliğin yapısı",
         "A + E", "Dış doğrulama kaynağı (sicil) gerekir"],
    ], st, ["Çerçeve", "Olası başlık", "İlgili alanlar", "Gereken ek çalışma"],
        [26 * mm, 60 * mm, 24 * mm, 60 * mm], small=True))
    GAP(2)
    NOTE("<b>Öneri.</b> Mevcut durumda <b>1. çerçeve</b> en az ek çalışma gerektirenidir: "
         "sistem çalışmakta, veri üretmekte ve yöntem belgelenmiş durumdadır. "
         "2. çerçeve daha yüksek etkili olabilir ancak çok şehirli bir veri toplama "
         "turu gerektirir; sistem bunu kaldıracak biçimde kuruludur.")

    # ---------- 7 ----------
    H1("7. Sistemin kapsamı ve sınırları (özet)")
    P("Ayrıntılı tartışma eşlik eden yöntem belgesindedir. Üst düzey özet:")
    GAP(1)
    s.append(table([
        ["Kapsam", f"{nsehir} Alman şehri, {nsektor} sektör; semt ya da tüm şehir düzeyinde tarama"],
        ["Veri kaynağı", "OpenStreetMap (ODbL) ve işletmelerin kendi herkese açık siteleri"],
        ["Ölçüm", "Beş nesnel engel kategorisi; öznel izlenimler ayrı tutulur"],
        ["Yöntem", "Deterministik; karar katmanında dil modeli yoktur, çıktı tekrarlanabilir"],
        ["Temel sınır", "Çerçeve OSM kapsamıyla sınırlıdır; evrene olasılıklı çıkarım yapılamaz"],
        ["Etik", "Yalnızca herkese açık veri; sistem kimseye otomatik ileti göndermez"],
    ], st, ["Başlık", "Durum"], [34 * mm, 136 * mm]))
    GAP(3)
    P("<i>Bu belge, çalışan bir kod tabanından türetilmiştir. Kapsam sayıları sistemin "
      "yapılandırmasından, örnek akış tablosu gerçek bir çalıştırmadan alınmıştır. "
      "Literatür başlıkları tarama için yön gösterici olarak sunulmuştur; kaynak "
      "taramasının kendisi bu belgenin kapsamı dışındadır.</i>")

    doc.build(s, onFirstPage=rpt._footer, onLaterPages=rpt._footer)
    print(f"Arastirma cercevesi hazir: {out}")
    return out


if __name__ == "__main__":
    build()
