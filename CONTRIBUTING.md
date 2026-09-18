# Katkı Rehberi

Katkıya açığım. Ancak bu projenin çift lisans modeli, katkılar konusunda
alışıldık açık kaynak projelerinden **farklı bir kural** gerektiriyor. Bir satır
kod göndermeden önce bunu okuyun.

---

## Neden özel bir kural var

LeadRadar iki lisansla dağıtılıyor: ticari olmayan kullanım için
[PolyForm Noncommercial 1.0.0](LICENSE), işletmeler için ayrı ve ücretli bir
ticari lisans ([COMMERCIAL.md](COMMERCIAL.md)).

Bir yazılımı ticari lisansla satabilmek için **o yazılımın tamamının telif
hakkına sahip olmak** gerekir. Kabul edilen bir katkının telifi katkıda
bulunanda kalırsa, proje sahibi o satırları ticari lisansa dahil edemez — ve
model çalışmaz.

Bu, katkınızın değersiz görüldüğü anlamına gelmez. Tam tersi: kodunuzun
satılabilir bir ürünün parçası olmasının yasal önkoşulu.

---

## Katkı Beyanı (DCO benzeri)

Bir pull request açarak aşağıdakileri beyan etmiş olursunuz:

1. Gönderdiğiniz katkı **sizin özgün eserinizdir**; başka bir kaynaktan
   kopyalanmamıştır. Başka bir kaynaktan alınan bir bölüm varsa, kaynağını ve
   lisansını PR açıklamasında belirtirsiniz.
2. Katkınız üzerindeki **mali hakları** (işleme, çoğaltma, yayma, temsil, umuma
   iletim — FSEK m.21-25) proje sahibi **Furkan Akduman**'a devredersiniz; ya da
   bu mümkün değilse, proje sahibine katkı üzerinde **süresiz, geri alınamaz,
   dünya çapında, alt lisans verilebilir ve münhasır olmayan** bir kullanım
   hakkı tanırsınız — **ticari lisanslama dahil.**
3. Bu devrin/iznin karşılığında bir ücret talep etmezsiniz.
4. İşvereniniz varsa ve katkı çalışma saatlerinizde veya işverenin
   ekipmanıyla üretildiyse, bu devri yapmaya yetkili olduğunuzu teyit
   etmiş olursunuz.

Bu beyanı PR açıklamasına şu satırı ekleyerek onaylayın:

```
Katkı Beyanı: CONTRIBUTING.md'deki koşulları okudum ve kabul ediyorum.
```

Bu satırı içermeyen pull request'ler birleştirilmez. Kişisel bir güvensizlik
değil; modelin çalışması için gereken belgedir.

---

## Katkı kabul edilmeyen durumlar

- **Beyan satırı yoksa** — yukarıdaki sebep
- **Kaynağı belirsiz kod** — başka bir projeden alınmış olabilecek, lisansı
  bilinmeyen bölümler
- **Copyleft lisanslı koddan türetilmiş katkı** (GPL, AGPL, LGPL) — bu
  lisanslar türev eserin de aynı lisansla dağıtılmasını zorunlu kılar ve
  ticari lisanslamayı imkânsız hâle getirir
- **Yeni bağımlılık ekleyen ve lisansı izin verici olmayan** katkılar
  (mevcut bağımlılıkların hepsi MIT/BSD'dir, bu bilinçli bir tercihtir)
- **Taramayı agresifleştiren katkılar** — bekleme sürelerini kaldıran, paralel
  istek sayısını artıran, `robots.txt` ya da kullanım koşullarını yok sayan
  değişiklikler. Yavaş ve nazik tarama bu projede bir tasarım kararıdır.

---

## Önce konuşalım

Büyük bir değişiklik planlıyorsanız **önce bir issue açın.** Reddedilecek bir
işe emek harcamanızı istemem. Küçük düzeltmeler (yazım hatası, açık bir bug,
belge iyileştirmesi) için doğrudan PR açabilirsiniz.

Özellikle ilgilendiğim katkılar:

- **Yeni ülkeler** — `city_catalog` ve `admin_level` eşlemeleri (Avusturya,
  İsviçre, Hollanda gibi OSM verisi güçlü ülkeler)
- **Yeni sektörler** — `category_osm` içine doğru OSM etiket eşlemesi
- **Yeni denetim kontrolleri** — `audit.py` içindeki desene uygun, **nesnel ve
  doğrulanabilir** olmak şartıyla. Öznel bir izlenim ekliyorsanız
  `heuristic_issues` tarafına koyun; guardrail'in bozulmaması esastır
- **Rapor iyileştirmeleri** — `report.py` içinde okunabilirlik ve baskı kalitesi

---

## Teknik beklentiler

- **Türkçe adlandırma.** Kullanıcıya görünen metinler ve yorumlar Türkçe;
  modül/fonksiyon adları mevcut kod tabanıyla tutarlı olsun.
- **Açıklama neden'i anlatsın.** Ne yaptığı koddan zaten okunuyor. Yorumlar
  *neden öyle yapıldığını* ve hangi tuzağı önlediğini anlatmalı.
- **Boru hattı bozulmasın.** PR'dan önce çalıştırın:
  ```
  py run.py --limit 2
  ```
  Yedi adım da tamam dönmeli ve PDF üretilmeli.
- **Puanlama guardrail'i korunsun.** Sezgisel bir bulgu tek başına asla YÜKSEK
  skor üretmemeli. Skorlama mantığına dokunuyorsanız bunu PR'da açıkça belirtin.
- **Yeni kaynak dosyalara telif başlığı ekleyin** — mevcut dosyalardaki
  SPDX bloğunu kopyalayın.

---

## Katkıda bulunanlar

Kabul edilen katkılar `TESEKKURLER.md` dosyasında adınızla anılır. Telif
devri, emeğin görünmez olması anlamına gelmez.
