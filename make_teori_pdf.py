# -*- coding: utf-8 -*-
# LeadRadar — yerel işletme lead keşif ve zenginleştirme sistemi
# Copyright (c) 2026 Furkan Akduman · https://github.com/FlyerFukas
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
#
# Ticari olmayan kullanım serbesttir (bkz. LICENSE).
# İşletmeler ve her türlü ticari kullanım ayrı, ücretli lisans gerektirir.
# Ayrıntı ve iletişim: COMMERCIAL.md
"""LeadRadar — Teorik Çerçeve ve Yöntem Belgesi (PDF üretici).

Akademik danışmana sunulmak üzere hazırlanmıştır: sistemin veriyi nereden
çektiği, neye göre sınıflandırdığı, hangi istatistiksel kabulleri yaptığı ve
hangi yanlılık kaynaklarını taşıdığı.

Kullanim:  py make_teori_pdf.py
Cikti:     docs/LeadRadar_Teorik_Cerceve.pdf
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
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from leadradar import report as rpt
from leadradar.config import load_config

NAVY = rpt.NAVY
GRID = rpt.GRID
LIGHT = rpt.LIGHT
ACCENT = colors.HexColor("#2d6cdf")

CFG = load_config(os.path.join(BASE_DIR, "config.json"))


def styles():
    rpt._register_fonts()
    st = rpt._styles()
    st["h1"] = ParagraphStyle("th1", fontSize=15.5, leading=20, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=10, spaceAfter=7)
    st["h2"] = ParagraphStyle("th2", fontSize=12, leading=16, fontName=rpt.FONT_BOLD,
                              textColor=NAVY, spaceBefore=9, spaceAfter=4)
    st["h3"] = ParagraphStyle("th3", fontSize=10.5, leading=14, fontName=rpt.FONT_BOLD,
                              textColor=colors.HexColor("#3a4263"), spaceBefore=7, spaceAfter=3)
    st["body"] = ParagraphStyle("tb", fontSize=9.8, leading=14.2, fontName=rpt.FONT,
                                textColor=colors.HexColor("#222230"), spaceAfter=5,
                                alignment=4)  # justify
    st["li"] = ParagraphStyle("tli", parent=st["body"], leftIndent=6 * mm, spaceAfter=3)
    st["note"] = ParagraphStyle("tn", fontSize=9.2, leading=13, fontName=rpt.FONT,
                                textColor=colors.HexColor("#4a5164"), leftIndent=5 * mm,
                                rightIndent=4 * mm, spaceBefore=4, spaceAfter=6,
                                borderPadding=6, backColor=colors.HexColor("#eef1f8"))
    st["form"] = ParagraphStyle("tf", fontSize=9.5, leading=14, fontName="Courier",
                                textColor=colors.HexColor("#11113a"),
                                backColor=colors.HexColor("#f0f1f6"),
                                borderPadding=6, leftIndent=4 * mm, spaceAfter=6, spaceBefore=3)
    return st


def table(rows, st, header, widths):
    th = ParagraphStyle("th", fontSize=9, leading=12, fontName=rpt.FONT_BOLD, textColor=colors.white)
    data = [[Paragraph(h, th) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), st["cell"]) for c in r])
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
    out = os.path.join(BASE_DIR, "docs", "LeadRadar_Teorik_Cerceve.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=16 * mm, bottomMargin=20 * mm,
                            title="LeadRadar — Teorik Çerçeve ve Yöntem Belgesi",
                            author="Furkan Akduman")
    s = []
    P = lambda t: s.append(Paragraph(t, st["body"]))
    H1 = lambda t: s.append(Paragraph(t, st["h1"]))
    H2 = lambda t: s.append(Paragraph(t, st["h2"]))
    H3 = lambda t: s.append(Paragraph(t, st["h3"]))
    LI = lambda t: s.append(Paragraph("• " + t, st["li"]))
    NOTE = lambda t: s.append(Paragraph(t, st["note"]))
    FORM = lambda t: s.append(Paragraph(t.replace(" ", "&nbsp;"), st["form"]))
    GAP = lambda h=3: s.append(Spacer(1, h * mm))

    nsehir = len(CFG["city_catalog"])
    nsektor = len(CFG["category_osm"])

    # ---------------- Kapak ----------------
    s.append(rpt._header_bar(
        "LeadRadar — Teorik Çerçeve ve Yöntem",
        f"Yerel işletme keşfi, kayıt eşleştirme ve kural tabanlı önceliklendirme "
        f"&nbsp;•&nbsp; {datetime.now().strftime('%d.%m.%Y')}", st))
    GAP(6)
    P("Bu belge, çalışan bir yazılım sisteminin <b>yöntemsel zeminini</b> akademik bir "
      "okuyucuya aktarmak için hazırlanmıştır. Amaç yazılımı tanıtmak değil; sistemin "
      "hangi veri kaynağından beslendiğini, veriyi hangi varsayımlarla sınıflandırdığını, "
      "hangi istatistiksel kabulleri yaptığını ve hangi yanlılık kaynaklarını taşıdığını "
      "açık biçimde ortaya koymaktır.")
    P("Belgedeki her parametre ve eşik, çalışan kod tabanından doğrudan okunmuştur; "
      "örnek sayılar gerçek çalıştırmalardan alınmıştır. Yöntem bölümlerinde sistemin "
      "<b>ne yaptığı</b> ile <b>neyi varsaydığı</b> bilinçli olarak ayrı tutulmuştur, "
      "çünkü makaleleştirmede tartışılması gereken asıl kısım ikincisidir.")
    NOTE("<b>Okuma notu.</b> Bölüm 3, 5 ve 6 yöntemsel çekirdeği oluşturur. "
         "Bölüm 10 (yanlılık ve geçerlilik) bir makalenin <i>limitations</i> bölümüne "
         "doğrudan karşılık gelecek biçimde yazılmıştır. Bölüm 11, henüz yanıtlanmamış "
         "ve ampirik olarak çalışılabilecek soruları listeler.")

    # ---------------- 1 ----------------
    H1("1. Problem tanımı")
    P("Sistem, bir coğrafi bölgedeki yerel işletmeler arasından <b>dijital varlığı zayıf "
      "olanları</b> belirlemeyi ve bunları öncelik sırasına koymayı amaçlar. Problem, "
      "klasik bir sınıflandırma probleminden iki noktada ayrılır.")
    P("Birincisi, <b>etiketli veri yoktur.</b> Bir işletmenin \"iyi aday\" olup olmadığına "
      "dair gözlenmiş bir sonuç değişkeni (satın aldı / almadı) mevcut değildir. Dolayısıyla "
      "denetimli öğrenme uygulanamaz; sınıflandırma ölçütleri dışarıdan tanımlanmak zorundadır.")
    P("İkincisi, <b>karar açıklanabilir olmak zorundadır.</b> Çıktı bir insana sunulup "
      "eyleme dönüştürüleceği için, her sınıflandırma kararının arkasında gösterilebilir "
      "bir gözlem bulunmalıdır. Bu kısıt, model seçimini doğrudan belirler.")
    P("Formal olarak: bir bölge <i>R</i> ve sektör kümesi <i>S</i> verildiğinde, işletme "
      "evreni <i>U(R,S)</i> üzerinden gözlenebilir bir çerçeve <i>F</i> oluşturulur; "
      "her birim için bir öznitelik vektörü <i>x<sub>i</sub></i> türetilir ve kural tabanlı "
      "bir fonksiyon <i>g(x<sub>i</sub>)</i> birimi sıralı üç sınıftan birine atar.")
    FORM("g : x → {YÜKSEK, ORTA, DÜŞÜK}   (sıralı / ordinal ölçek)")

    # ---------------- 2 ----------------
    H1("2. Boru hattının yapısı")
    P("Sistem altı aşamalı, tek yönlü bir veri hattıdır. Her aşama bir önceki aşamanın "
      "çıktısını daraltır; hiçbir aşama geriye besleme yapmaz. Bu, hattın her noktasında "
      "ara çıktının denetlenebilmesini sağlar.")
    GAP(1)
    s.append(table([
        ["1", "Çerçeve oluşturma", "Coğrafi sorgu ile aday birim listesi üretilir", "OpenStreetMap / Overpass API"],
        ["2", "Sınıflandırma", "OSM etiketleri sektör kategorilerine eşlenir", "Deterministik eşleme tablosu"],
        ["3", "Kayıt eşleştirme", "Tekrarlı birimler elenir, geçmiş kayıtla karşılaştırılır", "Hiyerarşik anahtar + SQLite"],
        ["4", "Örnek seçimi", "Kota ve çeşitlilik kuralıyla alt küme seçilir", "Amaçlı (purposive) seçim"],
        ["5", "Öznitelik çıkarımı", "Web sitesi gözlemlenir, göstergeler türetilir", "HTTP + HTML ayrıştırma"],
        ["6", "Önceliklendirme", "Kural tabanlı fonksiyon sınıf atar", "Eşik kuralı"],
    ], st, ["#", "Aşama", "İşlev", "Yöntem"], [8 * mm, 32 * mm, 70 * mm, 60 * mm]))
    GAP(2)
    NOTE("Aşama 1-4 <b>örnekleme</b>, aşama 5 <b>ölçüm</b>, aşama 6 <b>sınıflandırma</b> "
         "problemidir. Yanlılık tartışması bu üç kategoriye göre yapılmalıdır; "
         "çünkü her birinin hata kaynağı farklıdır.")

    # ---------------- 3 ----------------
    H1("3. Veri kaynağı ve örnekleme çerçevesi")
    H2("3.1 Kaynak: gönüllü coğrafi bilgi")
    P("Birincil veri kaynağı <b>OpenStreetMap</b>'tir ve veriye Overpass API üzerinden "
      "erişilir. OSM, gönüllü katkıyla üretilen bir coğrafi veri tabanıdır "
      "(literatürde <i>volunteered geographic information</i>, VGI). Bu, veri kalitesi "
      "açısından belirleyici bir niteliktir: kayıtlar merkezî bir otorite tarafından değil, "
      "dağıtık katkıcılar tarafından oluşturulur ve güncellenir.")
    P("Bir işletme OSM'de bir <i>node</i>, <i>way</i> ya da <i>relation</i> olarak bulunur "
      "ve anahtar-değer çiftlerinden oluşan etiketler taşır. Sistem için anlamlı olan "
      "alanlar şunlardır:")
    LI("<b>Kimlik:</b> <i>name</i> — etiketi olmayan kayıtlar çerçeveye alınmaz")
    LI("<b>Sınıf:</b> <i>shop</i>, <i>amenity</i>, <i>leisure</i>, <i>healthcare</i>, <i>office</i>, <i>tourism</i>")
    LI("<b>Konum:</b> <i>addr:street</i>, <i>addr:housenumber</i>, <i>addr:postcode</i>, <i>addr:city</i>")
    LI("<b>İletişim:</b> <i>phone</i> / <i>contact:phone</i>, <i>website</i> / <i>contact:website</i>")
    LI("<b>Bağlam:</b> <i>brand</i> (zincir göstergesi), <i>opening_hours</i>, <i>check_date</i>")

    H2("3.2 Coğrafi sınırlama ve idari hiyerarşi")
    P("Sorgu, serbest metin arama değil, <b>idari sınır poligonu</b> üzerinden yapılır. "
      "OSM'de idari birimler <i>admin_level</i> ile hiyerarşik olarak kodlanmıştır. Almanya'da "
      "şehir sınırının hangi seviyede tanımlandığı şehrin hukuki statüsüne bağlıdır ve bu, "
      "sorgunun doğruluğu açısından kritik bir ayrımdır:")
    GAP(1)
    s.append(table([
        ["4", "Şehir-eyalet (<i>Stadtstaat</i>)", "Berlin, Hamburg, Bremen", "3"],
        ["6", "İlçesiz şehir (<i>kreisfreie Stadt</i>)", "München, Köln, Leipzig, Nürnberg …", "24"],
        ["9 / 10", "Semt (<i>Stadtteil</i> / <i>Ortsteil</i>)", "Mitte, Neukölln, Kreuzberg …", "—"],
    ], st, ["admin_level", "Birim türü", "Örnek", "Katalogdaki şehir sayısı"],
        [24 * mm, 48 * mm, 62 * mm, 36 * mm]))
    GAP(2)
    P(f"Sistem {nsehir} Alman şehri için doğru seviyeyi bir katalogda tutar. Seviye yanlış "
      "seçilirse sorgu ya boş döner ya da aynı adı taşıyan daha geniş bir idari birimi "
      "(örneğin <i>Landkreis</i>) kapsayarak çerçeveyi şişirir. Bu, yöntemsel olarak "
      "<b>çerçeve tanımı hatası</b>dır ve sessizce gerçekleşir.")
    P("Semt listesi boş bırakılırsa tüm şehir tek sorguda taranır; semt verilirse önce şehir "
      "poligonu, sonra onun içindeki semt poligonu çözümlenir ve sorgu o alanla sınırlanır.")

    H2("3.3 Çerçeve ile evren arasındaki fark")
    P("Bu, belgenin en önemli yöntemsel noktasıdır. Sistem <b>gerçek işletme evrenini "
      "gözlemez</b>; yalnızca OSM'de kayıtlı olan ve <i>name</i> etiketi bulunan birimleri "
      "gözler. Dolayısıyla:")
    FORM("F (çerçeve) ⊆ U (evren),   ve  F ≠ U")
    P("Aradaki fark <b>kapsama hatası</b>dır (<i>coverage error</i>). İki yönü vardır: "
      "OSM'de hiç kaydı olmayan işletmeler çerçeve dışında kalır (<i>under-coverage</i>); "
      "kapanmış ama kaydı silinmemiş işletmeler çerçevede fazladan yer alır "
      "(<i>over-coverage</i>). Sistem bu farkı ölçmez ve ölçemez; çünkü karşılaştırılacak "
      "bir altın standart (örneğin ticaret sicili) veri setine erişimi yoktur.")
    NOTE("<b>Makale için açık soru.</b> OSM kapsama oranının sektöre ve şehir büyüklüğüne "
         "göre nasıl değiştiği ampirik olarak ölçülebilir: bir ilçe için resmî sicil "
         "kayıtlarıyla OSM kayıtları eşleştirilip kapsama oranı sektör bazında "
         "kestirilebilir. Bu, tek başına yayımlanabilir bir bulgudur ve sistemin "
         "güvenilirliğini de ölçülebilir kılar.")

    H2("3.4 Kesme (truncation) ve örneklem büyüklüğü")
    P("Overpass sorgusu bir çıktı sınırı ile çalışır. Tüm şehir taramasında bu sınır "
      f"{max(CFG['overpass_limit'], 200)}, semt taramasında {CFG['overpass_limit']} kayıttır. "
      "Sınırın altındaki bölgelerde dönen küme <b>tam sayımdır</b>; sınıra dayanan "
      "bölgelerde ise küme <b>kesilmiş (truncated)</b> bir alt kümedir.")
    P("Bu ayrım yorum açısından belirleyicidir: kesilmiş bir kümede hesaplanan oranlar "
      "(örneğin \"web sitesi olmayanların payı\") yalnızca <b>dönen küme için</b> geçerlidir. "
      "Overpass'ın döndürme sırası coğrafi/dahilî bir sıradır, rastgele değildir; bu nedenle "
      "kesilmiş küme basit rastgele örneklem sayılamaz. Raporlanan oranlar bu yüzden "
      "\"200 sonuçluk örneklem\" ifadesiyle birlikte verilmelidir.")

    # ---------------- 4 ----------------
    H1("4. Sınıflandırma şeması: etiketten sektöre")
    P(f"OSM etiketleri {nsektor} sektör kategorisine eşlenir. Eşleme <b>deterministik ve "
      "çoktan-bire</b>dir: bir kategoriye birden çok etiket çifti karşılık gelebilir, ama bir "
      "etiket çifti tek bir kategoriye bağlanır.")
    GAP(1)
    s.append(table([
        ["Friseur (kuaför)", "shop=hairdresser", "Tekil eşleme"],
        ["Restaurant", "amenity=restaurant", "Tekil eşleme"],
        ["Zahnarzt (diş hekimi)", "amenity=dentist <b>veya</b> healthcare=dentist", "Çoklu etiket, aynı kategori"],
        ["Arzt (hekim)", "amenity=doctors <b>veya</b> healthcare=doctor", "Çoklu etiket, aynı kategori"],
        ["Bar/Kneipe", "amenity=bar <b>veya</b> amenity=pub", "Birleştirilmiş kategori"],
    ], st, ["Kategori", "OSM etiket koşulu", "Eşleme tipi"], [40 * mm, 76 * mm, 54 * mm]))
    GAP(2)
    P("Ölçek düzeyi <b>nominal</b>dir; kategoriler arasında sıra ya da uzaklık tanımlı değildir. "
      "Kategori ataması, seçilmiş kategori listesi üzerinde ilk eşleşen etikete göre yapılır; "
      "bu nedenle aynı etiketi paylaşan iki kategori birlikte seçilirse atama, listedeki sıraya "
      "bağlı hale gelir. Bu bilinen ve belgelenmiş bir sınırlamadır.")

    H2("4.1 Zincir ve franchise elemesi")
    P("Hedef kitle bağımsız yerel işletmelerdir; zincirler analiz dışıdır. Eleme iki ölçüte "
      "dayanır ve ikisi de <b>veri temelli</b>dir, sezgisel değildir:")
    LI("OSM kaydında <i>brand</i> ya da <i>brand:wikidata</i> etiketinin bulunması — "
       "bu etiket, kaydın bir markaya ait olduğunun OSM topluluğu tarafından doğrulanmış göstergesidir")
    LI(f"İsmin, {len(CFG['chain_blacklist'])} girdilik bir kara listede geçmesi — "
       "marka etiketi eksik bırakılmış kayıtlar için ikincil güvence")
    P("Birinci ölçüt yüksek kesinlikte (<i>precision</i>) çalışır; ikincisi duyarlılığı "
      "(<i>recall</i>) artırır ama yanlış pozitif üretebilir: kara listedeki bir sözcüğü "
      "tesadüfen içeren bağımsız bir işletme elenebilir. Bu, bilinçli bir takastır.")

    # ---------------- 5 ----------------
    H1("5. Kayıt eşleştirme ve tekilleştirme")
    P("Aynı işletmenin birden fazla kez işleme girmesi iki nedenle olur: aynı tarama içinde "
      "farklı etiketlerle iki kez dönmesi, ya da önceki haftalarda zaten raporlanmış olması. "
      "Her iki durum da <b>kayıt eşleştirme</b> (<i>record linkage</i>) problemidir.")

    H2("5.1 Normalizasyon")
    P("Karşılaştırma öncesinde metin alanları standartlaştırılır: küçük harfe çevirme, "
      "ardışık boşlukların tekleştirilmesi, harf ve rakam dışındaki karakterlerin atılması. "
      "Web adresleri için yalnızca alan adı alınır ve <i>www.</i> öneki düşürülür. "
      "Bu adım, biçim farklılıklarının yapay uyuşmazlık üretmesini engeller.")

    H2("5.2 Hiyerarşik anahtar")
    P("Sistem olasılıksal değil <b>deterministik</b> eşleştirme kullanır. Anahtar, mevcut "
      "alanlara göre azalan güvenilirlik sırasıyla seçilir:")
    FORM("1. ad | adres     2. ad | telefon     3. ad | alan adı     4. ad |")
    P("Sıra tesadüfi değildir. Adres, bir işletmeyi konumuyla birlikte tanımladığı için en "
      "ayırt edici alandır. Telefon ikinci sıradadır çünkü paylaşımlı numaralar seyrek de olsa "
      "görülür. Alan adı üçüncüdür çünkü aynı alan adı birden çok şubeye ait olabilir. "
      "Yalnızca ada düşen dördüncü düzey en zayıf halkadır ve farklı iki işletmeyi "
      "birleştirme riski taşır.")

    H2("5.3 Hata tipleri")
    GAP(1)
    s.append(table([
        ["Yanlış birleştirme (<i>false match</i>)",
         "Farklı iki işletme aynı anahtarı üretir",
         "Gerçek bir aday sessizce elenir; çıktıda görünmez, bu yüzden fark edilmesi zordur"],
        ["Kaçırılan eşleşme (<i>false non-match</i>)",
         "Aynı işletme farklı yazımlarla iki anahtar üretir",
         "Aynı işletme tekrar raporlanır; kullanıcı fark eder, maliyeti düşüktür"],
    ], st, ["Hata", "Nasıl oluşur", "Sonucu"], [44 * mm, 52 * mm, 74 * mm]))
    GAP(2)
    P("Hiyerarşik tasarım bilinçli olarak <b>ikinci hata tipine toleranslı</b>dır. Bir aday "
      "yanlışlıkla elenirse bir daha asla görünmez; tekrar görünmesi ise yalnızca bir "
      "rahatsızlıktır. Olasılıksal eşleştirme (Fellegi-Sunter türü bir ağırlıklandırma) daha "
      "yüksek doğruluk verebilirdi, ancak eşik kalibrasyonu için etiketli bir eşleşme kümesi "
      "gerekir; böyle bir küme mevcut değildir.")
    NOTE("<b>Makale için açık soru.</b> Bir alt küme elle etiketlenerek deterministik "
         "anahtarın kesinlik ve duyarlılığı ölçülebilir; ardından aynı küme üzerinde "
         "olasılıksal eşleştirme ile karşılaştırma yapılabilir. Yerel işletme verisinde "
         "kayıt eşleştirme kalitesi, kendi başına çalışılmaya değer bir konudur.")

    # ---------------- 6 ----------------
    H1("6. Eksik veri mi, gözlenmiş yokluk mu?")
    P("Sistemin en kritik varsayımı buradadır ve akademik tartışmaya en açık nokta budur.")
    P("Bir OSM kaydında <i>website</i> alanı boşsa, bunun iki farklı anlamı olabilir: "
      "(a) işletmenin gerçekten web sitesi yoktur, (b) işletmenin sitesi vardır ama "
      "OSM'ye kimse girmemiştir. Sistem bu alanı <b>gözlenmiş bir yokluk</b> olarak yorumlar "
      "ve ilgili birimi en yüksek önceliğe atar.")
    P("İstatistiksel dille: boşluk bir <b>eksik veri</b> olabilir ve eksiklik mekanizması "
      "büyük olasılıkla <i>tamamen rastgele</i> (MCAR) değildir. Küçük, az ziyaret edilen ya da "
      "dijital varlığı zaten zayıf işletmelerin OSM kaydının da eksik tutulmuş olması "
      "muhtemeldir. Yani eksiklik, ölçmek istediğimiz değişkenin kendisiyle ilişkilidir; "
      "bu durum <i>missing not at random</i> (MNAR) tanımına yaklaşır.")
    NOTE("<b>Yorum.</b> Bu durum sistemin pratik amacı açısından paradoksal biçimde "
         "zararsız olabilir: eksikliğin kendisi \"dijital varlığı zayıf\" sinyaliyle aynı "
         "yönde ilişkiliyse, hedefleme yine doğru kitleye yönelir. Ancak bu bir "
         "<b>tesadüfi tutarlılıktır, yöntemsel bir gerekçe değildir.</b> Ölçüm "
         "geçerliliği iddiası kurulacaksa bu ilişkinin ampirik olarak gösterilmesi gerekir.")
    P("Doğrulanabilir bir tasarım şöyle kurulabilir: web sitesi alanı boş olan bir birim "
      "örneklemi için bağımsız bir arama yapılır (arama motoru ya da ticaret sicili) ve "
      "gerçekten site olup olmadığı tespit edilir. Elde edilen oran, sistemin yanlış pozitif "
      "oranını doğrudan ölçer ve MNAR varsayımını sınar.")

    # ---------------- 7 ----------------
    H1("7. Öznitelik çıkarımı: web sitesinin ölçülmesi")
    P("Sitesi bulunan birimler için site fiilen talep edilir ve HTML'i ayrıştırılır. "
      "Amaç, \"kötü site\" gibi öznel bir yargı değil, <b>ikili ve doğrulanabilir "
      "göstergeler</b> üretmektir. Beş nesnel engel kategorisi tanımlıdır:")
    GAP(1)
    s.append(table([
        ["Erişilebilirlik", "Sayfa yüklenmiyor, HTTP ≥ 400, boş gövde, sonsuz yönlendirme",
         "Bağlantı denemesi ve durum kodu"],
        ["Aktarım güvenliği", "HTTPS yok ya da sertifika geçersiz", "Şema denetimi ve TLS doğrulaması"],
        ["Mobil uyumluluk", "<i>viewport</i> meta etiketi yok", "DOM sorgusu"],
        ["İletişim yolu", "Telefon, e-posta ya da iletişim bağlantısı yok; ya da bağlantı hata veriyor",
         "Bağlantı ve metin desenleri, ardından bağlantı denemesi"],
        ["Randevu yolu", "Rezervasyon bağlantısı ölü", "Bağlantı denemesi"],
    ], st, ["Kategori", "Gösterge", "Ölçüm yöntemi"], [32 * mm, 76 * mm, 62 * mm]))
    GAP(2)
    P("Her kategori <b>en çok bir kez</b> sayılır. Bu, aynı kök nedenin skoru şişirmesini "
      "engeller: tek bir sertifika hatası hem HTTPS hem erişilebilirlik sorununa yol açsa bile "
      "iki ayrı engel olarak sayılmaz. Toplam engel sayısı bu nedenle 0 ile 5 arasındadır.")

    H2("7.1 Nesnel ile sezgiselin ayrılması")
    P("Sistem ikinci bir gösterge kümesi daha üretir ve bunları <b>ayrı bir alanda</b> tutar: "
      "alt bilgideki eski telif yılı, çok eski kütüphane sürümleri, eksik meta açıklama, "
      "Flash içeriği. Bunlar <i>[HEURISTIC]</i> önekiyle işaretlenir.")
    P("Bu ayrım bir <b>yapı geçerliliği</b> (<i>construct validity</i>) önlemidir. Ölçülmek "
      "istenen yapı \"işletmenin dijital varlığında somut, gösterilebilir bir eksiklik\"tır. "
      "\"Site eski görünüyor\" ifadesi bu yapıyı ölçmez; ölçenin estetik yargısını ölçer. "
      "İkisi aynı havuza konulsaydı skor, gözlemciye göre değişen bir büyüklük haline gelirdi.")

    # ---------------- 8 ----------------
    H1("8. Önceliklendirme fonksiyonu")
    P("Sınıf ataması, kural tabanlı ve tamamen deterministik bir fonksiyonla yapılır:")
    GAP(1)
    s.append(table([
        ["Web sitesi kaydı yok", "—", "<b>YÜKSEK</b>"],
        ["Yalnızca sosyal medya sayfası var", "—", "<b>YÜKSEK</b>"],
        ["Site var", "engel sayısı ≥ 2", "<b>YÜKSEK</b>"],
        ["Site var", "engel sayısı = 1", "<b>ORTA</b>"],
        ["Site var", "engel = 0, sezgisel bulgu ≥ 2", "<b>ORTA</b>"],
        ["Site var", "engel = 0, sezgisel bulgu &lt; 2", "<b>DÜŞÜK</b>"],
    ], st, ["Durum", "Koşul", "Sınıf"], [60 * mm, 60 * mm, 50 * mm]))
    GAP(2)
    P("Kuralın değişmez niteliği şudur: <b>sezgisel bulgular tek başına YÜKSEK sınıf "
      "üretemez.</b> En fazla ORTA'ya taşıyabilir. Böylece en yüksek öncelikli her birimin "
      "arkasında ya gözlenmiş bir yokluk ya da en az iki doğrulanmış engel bulunur.")

    H2("8.1 Neden olasılıksal bir model kullanılmadı")
    P("Üç gerekçe vardır. <b>Birincisi</b>, hedef değişken yoktur; denetimli bir modelin "
      "öğreneceği bir sonuç gözlenmemiştir. <b>İkincisi</b>, açıklanabilirlik işlevsel bir "
      "zorunluluktur: çıktı bir satış görüşmesinde kullanılacaksa, \"model 0,78 olasılık "
      "verdi\" cümlesi kullanılamaz; \"siteniz http üzerinden yayında ve telefonda "
      "okunmuyor\" cümlesi kullanılabilir. <b>Üçüncüsü</b>, kural tabanlı sistem tam "
      "tekrarlanabilirdir; aynı girdi her zaman aynı çıktıyı verir.")
    NOTE("<b>Makale için açık soru.</b> Eşik değerinin (≥ 2 engel) seçimi şu an kuramsal "
         "değil, pratik bir karardır. Gerçek dönüşüm verisi toplandığında, engel sayısı ile "
         "dönüşüm arasındaki ilişki ölçülebilir ve eşik ampirik olarak kalibre edilebilir. "
         "Bu aşamada sıralı lojistik regresyon doğal bir karşılaştırma modelidir.")

    # ---------------- 9 ----------------
    H1("9. Örnekleme tasarımı")
    H2("9.1 Kota ve çeşitlilik")
    P(f"Çerçeveden önce {CFG['discover_pool']} birimlik bir havuz, ardından "
      f"{CFG['target_leads']} birimlik nihai küme seçilir. Seçim rastgele değil, "
      "<b>kotalıdır</b>: havuzun ve nihai kümenin yaklaşık "
      f"%{int(CFG['no_website_ratio'] * 100)}'ı web sitesi hiç olmayan birimlerden oluşur. "
      "Kalan kısım, zayıf dijital varlık sırasına göre doldurulur: önce yalnızca sosyal medya "
      "sayfası olanlar, sonra http üzerinden yayın yapanlar, en son normal siteye sahip olanlar.")
    P("Aynı katman içinde <b>dönüşümlü (round-robin) seçim</b> uygulanır: kategori ve semt "
      "çiftleri sırayla dolaşılır. Bu, nihai kümenin tek bir sektöre ya da tek bir mahalleye "
      "yığılmasını engeller. İstatistiksel karşılığı <b>tabakalı seçimdir</b>, ancak tabaka "
      "içi seçim rastgele değil, bilgi bütünlüğü sırasına göredir.")
    NOTE("<b>Çıkarım sınırı.</b> Bu tasarım <b>amaçlı örneklemdir</b> (<i>purposive</i>), "
         "olasılıklı örneklem değildir. Dolayısıyla nihai kümeden evrene yönelik "
         "<b>olasılıklı çıkarım yapılamaz</b>: güven aralığı ya da hipotez testi bu küme "
         "üzerinden kurulamaz. Evren hakkında oran kestirimi gerekiyorsa, kota uygulanmamış "
         "ham çerçeve kullanılmalıdır. Belgedeki Münih ve Köln oranları bu nedenle nihai "
         "kümeden değil, ham çerçeveden hesaplanmıştır.")

    H2("9.2 Dönüşümlü panel yapısı")
    P("Haftalık otomatik çalıştırmada kategori ve bölge kümeleri, yılın hafta numarasının "
      "4'e bölümünden kalana göre dört blok arasında döner. Bu, anket metodolojisindeki "
      "<b>dönüşümlü panel</b> (<i>rotating panel</i>) tasarımına benzer bir yapıdır: "
      "her dönem farklı bir alt evren gözlenir, böylece aynı birimlerin tekrar tekrar "
      "örneklenmesi önlenir ve zaman içinde kapsama genişler.")
    GAP(1)
    rot_rows = []
    for i, (cats, areas) in enumerate(zip(CFG["category_rotation"], CFG["area_rotation"])):
        rot_rows.append([f"hafta mod 4 = {i}", ", ".join(cats), ", ".join(areas)])
    s.append(table(rot_rows, st, ["Blok", "Sektörler", "Bölgeler"], [30 * mm, 66 * mm, 74 * mm]))
    GAP(2)
    P("Rotasyon ile tekilleştirme birlikte çalışır: rotasyon <b>yeni alan</b> açar, "
      "tekilleştirme <b>tekrarı engeller</b>. İkisi olmadan sistem birkaç hafta içinde "
      "aynı birimleri döndürmeye başlardı.")

    # ---------------- 10 ----------------
    H1("10. Yanlılık, geçerlilik ve sınırlar")
    P("Aşağıdaki tablo, bir makalenin <i>limitations</i> bölümüne doğrudan taşınabilecek "
      "biçimde düzenlenmiştir. Her satır, hatanın hangi aşamada doğduğunu gösterir.")
    GAP(1)
    s.append(table([
        ["Kapsama", "Çerçeve (1)",
         "OSM'de kaydı olmayan işletme hiç gözlenmez; eksiklik rastgele dağılmamış olabilir"],
        ["Kesme", "Çerçeve (1)",
         "Sorgu sınırına dayanan bölgelerde dönen küme kesilmiştir; sıra rastgele değildir"],
        ["Sınıflandırma", "Eşleme (2)",
         "Etiketi eksik ya da yanlış girilmiş birim yanlış kategoriye düşer ya da hiç görünmez"],
        ["Eleme", "Eşleme (2)",
         "Kara liste tabanlı zincir elemesi bağımsız işletmeyi yanlışlıkla eleyebilir"],
        ["Eşleştirme", "Tekilleştirme (3)",
         "Zayıf anahtar düzeyinde farklı işletmeler birleşebilir; eleme sessizdir"],
        ["Seçim", "Örnekleme (4)",
         "Kota, nihai kümeyi bilinçli olarak çarpıtır; evren oranı kestirilemez"],
        ["Ölçüm", "Öznitelik (5)",
         "Tek anlık gözlem; geçici kesinti kalıcı sorun gibi görünebilir"],
        ["Ölçüm", "Öznitelik (5)",
         "Bot koruması ya da JS ile üretilen içerik, siteyi olduğundan zayıf gösterebilir"],
        ["Zaman", "Tümü",
         "OSM kaydı güncel olmayabilir; kapanmış işletme çerçevede kalabilir"],
        ["Dışsal geçerlilik", "Tümü",
         "Parametreler Almanya idari yapısına göre ayarlanmıştır; doğrudan genellenemez"],
    ], st, ["Yanlılık türü", "Doğduğu aşama", "Açıklama"], [30 * mm, 30 * mm, 110 * mm]))

    H2("10.1 Ölçülmüş değerler")
    P("Aşağıdaki oranlar, kota uygulanmamış <b>ham çerçeve</b> üzerinden hesaplanmıştır ve "
      "sistemin gerçek çalıştırmalarından alınmıştır. Her şehir için 200 sonuçluk bir "
      "örneklem söz konusudur; oranlar bu küme için geçerlidir, şehrin tamamına "
      "genellenemez.")
    GAP(1)
    s.append(table([
        ["München", "Friseur (kuaför)", "196", "142", "%72"],
        ["Köln", "Friseur (kuaför)", "195", "153", "%78"],
    ], st, ["Şehir", "Sektör", "Çerçevedeki birim", "Web sitesi yok", "Oran"],
        [30 * mm, 46 * mm, 32 * mm, 32 * mm, 30 * mm]))
    GAP(2)
    P("Bu iki gözlem, dijital varlık eksikliğinin yerel hizmet sektöründe <b>marjinal değil "
      "baskın</b> bir durum olduğunu düşündürmektedir. Ancak yukarıdaki kapsama ve kesme "
      "uyarıları nedeniyle bu oranlar bir evren kestirimi olarak sunulamaz; yalnızca "
      "problemin büyüklüğüne dair bir gösterge niteliğindedir.")

    # ---------------- 11 ----------------
    H1("11. Belirlenimcilik ve yapay zekânın konumu")
    P("Sistemin mimari kararı şudur: <b>yapay zekâ karar katmanında bulunmaz.</b> "
      "Keşif, sınıflandırma, eşleştirme, ölçüm ve önceliklendirme aşamalarının tamamı "
      "deterministik kodla yürütülür. Dil modeli yalnızca isteğe bağlı bir metin cilası "
      "olarak, üretilmiş bulguların ifadesini düzenlemek için devreye alınabilir ve "
      "<b>skorları değiştiremez</b>.")
    P("Bu tercih, projenin kökeniyle ilgilidir. Çıkış noktası, aynı işi iki dil modeli "
      "ajanıyla yapan bir akış otomasyonuydu. İnceleme sonucunda, modele sorulan soruların "
      "neredeyse tamamının <b>kodla ölçülebilir nesnel kontroller</b> olduğu görüldü: "
      "\"sayfada viewport etiketi var mı\" sorusunun bir dil modeline sorulması için "
      "yöntemsel bir gerekçe yoktur.")
    P("Yöntemsel kazanç üç başlıkta toplanır:")
    LI("<b>Tekrarlanabilirlik.</b> Aynı girdi ve aynı tarih için çıktı birebir aynıdır; "
       "bir sonucun doğrulanması mümkündür")
    LI("<b>Denetlenebilirlik.</b> Her sınıf atamasının arkasında, kodda izlenebilir bir "
       "kural ve gözlenmiş bir gösterge vardır")
    LI("<b>Halüsinasyon riskinin yokluğu.</b> Üretilmiş hiçbir olgu yoktur; tüm bulgular "
       "ya OSM kaydından ya da HTTP yanıtından türetilmiştir")
    NOTE("<b>Makale için çerçeve önerisi.</b> Bu karşıtlık, yayın için verimli bir eksen "
         "oluşturur: aynı görevi (a) dil modeli ajanlarıyla ve (b) kural tabanlı "
         "deterministik bir hatla çözen iki sistemin, <b>tutarlılık</b> (aynı girdide "
         "tekrar oranı), <b>doğruluk</b> (elle doğrulanmış alt küme üzerinde) ve "
         "<b>maliyet</b> açısından karşılaştırılması. Literatürde uygulamalı ve ölçülmüş "
         "bu tür karşılaştırmalar görece azdır.")

    # ---------------- 12 ----------------
    H1("12. Açık sorular")
    P("Aşağıdaki sorular sistem tarafından yanıtlanmamıştır ve ampirik çalışmaya açıktır. "
      "Her biri, mevcut kod tabanı üzerinden veri üretilerek incelenebilir.")
    LI("<b>Kapsama.</b> OSM kapsama oranı sektöre, şehir büyüklüğüne ve bölgeye göre nasıl "
       "değişir? Resmî bir sicil ile eşleştirme yapılabilir mi?")
    LI("<b>Eksiklik mekanizması.</b> Boş <i>website</i> alanı ne sıklıkla gerçek bir yokluğa "
       "karşılık geliyor? Yanlış pozitif oranı nedir ve işletme büyüklüğüyle ilişkili mi?")
    LI("<b>Eşleştirme kalitesi.</b> Deterministik hiyerarşik anahtarın kesinlik ve duyarlılığı "
       "nedir? Olasılıksal eşleştirme ne kadar iyileştirir?")
    LI("<b>Eşik kalibrasyonu.</b> Engel sayısı ile gerçek dönüşüm arasındaki ilişki nedir? "
       "Sıralı bir model, kural tabanlı eşikten daha iyi ayrım yapar mı?")
    LI("<b>Gösterge geçerliliği.</b> Beş nesnel engel, işletmenin dijital performansıyla "
       "(örneğin arama görünürlüğü) ilişkili mi? Hangi gösterge en çok bilgi taşıyor?")
    LI("<b>Zamansal kararlılık.</b> Aynı bölge altı ay arayla tarandığında bulgular ne kadar "
       "değişir? Değişim gerçek mi, yoksa ölçüm gürültüsü mü?")

    H1("13. Teknik künye")
    GAP(1)
    s.append(table([
        ["Veri kaynağı", "OpenStreetMap, Overpass API (ODbL lisanslı)"],
        ["Kapsam", f"{nsehir} Alman şehri, {nsektor} sektör kategorisi"],
        ["Dil ve kütüphaneler", "Python 3.10+, requests, BeautifulSoup, ReportLab, SQLite"],
        ["Kalıcılık", "SQLite; parmak izi tablosu tekilleştirme belleği olarak"],
        ["Belirlenimcilik", "Karar katmanında dil modeli yok; çıktı tekrarlanabilir"],
        ["Tarama etiği", "İstekler arası bekleme, site başına tek istek, yalnızca herkese açık veri"],
        ["Kaynak kodu", "github.com/FlyerFukas/leadradar (kaynağı açık, ticari kullanım lisanslı)"],
    ], st, ["Başlık", "Değer"], [44 * mm, 126 * mm]))
    GAP(3)
    P("<i>Bu belge, çalışan bir kod tabanından türetilmiştir. Belirtilen tüm parametreler "
      "ve eşikler sistemin yapılandırmasından doğrudan okunmuş, oranlar gerçek "
      "çalıştırmalardan alınmıştır. Yöntemsel iddialar sistemin ne yaptığıyla sınırlıdır; "
      "evrene yönelik genellemeler bu belgenin kapsamı dışındadır.</i>")

    doc.build(s, onFirstPage=rpt._footer, onLaterPages=rpt._footer)
    print(f"Teorik cerceve hazir: {out}")
    return out


if __name__ == "__main__":
    build()
