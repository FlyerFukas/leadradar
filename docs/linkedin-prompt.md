# Claude Chat'e yapıştırılacak PROMPT

> Aşağıdaki çerçevenin tamamını (bu satırın altındaki her şeyi) kopyalayıp Claude Chat'e yapıştır.
> Sistem rehberi PDF'ini ayrıca eklemene gerek yok — gereken tüm bilgi promptun içinde.

---

Merhaba. Senden bir LinkedIn gönderisi yazmanı istiyorum. Önce iki şeyi yap:

1. `humanizer` skill'ini çağır ve gönderiyi o kurallara göre yaz.
2. Aşağıdaki brief'i sonuna kadar oku, sonra yazmaya başla.

---

## KİMİM, NE İSTİYORUM

Ben Furkan Akduman. Ticari ve gündelik hayat problemlerine **yapay zekâ destekli dijital çözümler** geliştiriyorum. Bu gönderinin amacı bir proje duyurusu değil; **"bu adam gerçek bir problemi görüp uçtan uca çözüyor" izlenimini bırakmak.** Gönderiyi okuyan kişi şunu düşünmeli: *"Bu kişi bizim de bir problemimizi çözebilir."*

Gönderide açıkça ama **övünmeden** geçmesi gereken üç mesaj:
- Ticari bir probleme somut bir çözüm ürettim.
- Bunu **yapay zekâ ile birlikte** geliştirdim (AI ile çalışmayı biliyorum, bunu saklamıyorum — tersine, bu bir yetkinlik).
- Bu bir **AI otomasyon projesi**: karar verme kısmında yapay zekâ, doğrulama kısmında deterministik kod var.

**Yaz:** Türkçe. Sonunda ayrıca kısa bir İngilizce sürüm ver (uluslararası bağlantılarım için).

**GitHub linki:** https://github.com/FlyerFukas/leadradar

---

## ÇÖZDÜĞÜM TİCARİ PROBLEM

Serbest web tasarımcıları, dijital ajanslar ve yerel B2B satış ekipleri için müşteri adayı bulmak hâlâ elle yapılan bir iş. Somut acılar:

1. **Elle arama çok yavaş.** Haritalarda tek tek geziniyorsun, her işletmenin sitesini açıp çalışıp çalışmadığına bakıyorsun. Birkaç kullanılabilir aday için saatler gidiyor.
2. **"Sitesi yok" ile "sitesi var ama müşteri kaybettiriyor" ayırt edilemiyor.** İkincisi gözle görünmüyor; siteyi açıp teknik olarak test etmen gerekiyor.
3. **Öznel yargı satılamıyor.** "Siteniz eski görünüyor" demek bir satış argümanı değil. "Siteniz http üzerinden yayında, telefonda okunmuyor ve iletişim sayfanız hata veriyor" demek satış argümanı.
4. **Hafıza yok.** Geçen ay aradığın işletmeyi bu ay tekrar arıyorsun. Hem zaman kaybı hem itibar kaybı.
5. **Çıktı eyleme dönüşmüyor.** Elinde isim listesi kalıyor; kimi, hangi kanaldan, hangi cümleyle arayacağın belli değil.

**Gerçek ölçüm (kendi taramalarımdan, uydurma istatistik değil):**
- Münih, kuaförler: 196 işletme bulundu, **142'sinin hiç web sitesi yok (%72)**
- Köln, kuaförler: 195 işletme bulundu, **153'ünün hiç web sitesi yok (%78)**
- (Her şehir için 200 sonuçluk örneklem üzerinden.)

Bunun üstüne bir de *sitesi olan ama pratikte çalışmayan* işletmeler geliyor — http üzerinden yayınlananlar, telefonda açılmayanlar, iletişim formu hata verenler. Bunlar elle prospecting'de tamamen görünmez.

---

## ÇÖZÜM: LeadRadar

Bir şehir ve sektör seçiyorsun; sistem o bölgedeki **web sitesi olmayan ya da sitesi bozuk** işletmeleri buluyor, kanıta dayalı puanlıyor ve satış görüşmesine hazır bir **PDF rapor** üretiyor.

### Nasıl çalışıyor (boru hattı)

```
Şehir/sektör seçimi (panel)
   ↓
Keşif — OpenStreetMap Overpass API (GPS koordinatlı işletme kayıtları)
   ↓
Parmak izi + tekilleştirme (SQLite hafıza)
   ↓
Seçim — önce sitesi hiç olmayanlar
   ↓
Web sitesi denetimi (teknik testler)
   ↓
Puanlama — YÜKSEK / ORTA / DÜŞÜK, yalnızca kanıtla
   ↓
Kayıt + PDF rapor
```

### Teknik ayrıntılar (gönderide hepsini kullanma, en çarpıcı 4-5 tanesini seç)

**Keşif katmanı**
- Veri kaynağı **OpenStreetMap Overpass API** — işletmeler GPS koordinatlı coğrafi kayıtlardan çekiliyor, API anahtarı gerekmiyor, ücretsiz.
- **27 Alman şehri**, **25 sektör** (kuaför, restoran, diş hekimi, eczane, emlakçı, oto tamir, avukat, veteriner, otel…).
- Şehir sınırı sorgusu OSM `admin_level` hiyerarşisini doğru kullanıyor: Berlin/Hamburg/Bremen gibi şehir-eyaletleri ile normal "kreisfreie Stadt"lar farklı seviyelerde tanımlı — sistem her şehir için doğru seviyeyi biliyor.
- Semt seçilirse o semt, seçilmezse **tüm şehir** tek sorguda taranıyor.
- **Zincir/franchise otomatik eleniyor**: OSM `brand` etiketi olan kayıtlar + isim kara listesi.
- Overpass sunucusu meşgulse (429/504) otomatik bekleyip **yedek uca geçiyor** — bir semt düşse bile tarama devam ediyor.

**Tekilleştirme (bence en değerli ve en az konuşulan kısım)**
- Her işletme için normalize edilmiş bir **parmak izi** üretiliyor: `isim|adres` → yoksa `isim|telefon` → yoksa `isim|alan-adı`. Büyük/küçük harf, noktalama, boşluk farkları temizleniyor.
- Bu parmak izleri SQLite'ta tutuluyor; sonraki taramada **daha önce raporlanan işletme bir daha gelmiyor.**
- Ayrıca haftalık rotasyon var: hafta numarasına göre her hafta farklı kategori + semt kombinasyonu taranıyor, aynı bölgede dönüp durmuyorsun.

**Web sitesi denetimi — asıl teknik iş burada**
Sitesi olan her adayın sitesi gerçekten açılıp test ediliyor. Tespit edilen **nesnel engeller**:
- **HTTPS yok** — site şifrelenmemiş http üzerinden yayında (ya da SSL sertifikası geçersiz)
- **Mobil uyumsuz** — `viewport` meta etiketi yok, yani telefonda okunmuyor
- **İletişim yolu kopuk** — sayfada telefon (`tel:`), e-posta (`mailto:`) veya iletişim linki bulunamıyor; ya da iletişim sayfası **404 veriyor**
- **Randevu/rezervasyon yolu bozuk** — sitedeki randevu linki ölü (Doctolib, OpenTable, Treatwell, Jameda gibi dış platformlar tanınıyor ve ayrı tutuluyor)
- **Sayfa hataları** — site hiç açılmıyor, boş sayfa, sunucu hatası, sonsuz yönlendirme döngüsü
- Ayrıca **teknoloji parmak izi** çıkarılıyor: WordPress / Wix / Jimdo / TYPO3 / Joomla tespiti, jQuery sürümü — ve **güncellik sinyali**: alt bilgideki telif yılı, sunucunun `Last-Modified` başlığı, OSM kayıt tarihi.

**Puanlama — projenin ahlaki omurgası**
- **YÜKSEK**: sitesi hiç yok **veya** en az **iki doğrulanmış nesnel engel** var
- **ORTA**: tek engel, ya da birden çok sezgisel bulgu
- **DÜŞÜK**: site sağlıklı — öncelikten düşür
- **Kritik kural:** "site eski görünüyor", "tasarım zayıf" gibi **öznel izlenimler ayrı bir alanda `[HEURISTIC]` etiketiyle tutuluyor ve tek başlarına ASLA YÜKSEK puan üretemiyor.** Yani rapordaki her yüksek puanın arkasında test edilmiş, gösterilebilir bir kanıt var.
- Sistem **deterministik**: aynı girdi her zaman aynı çıktıyı veriyor. Halüsinasyon yok, "bu sefer başka dedi" yok.

**Çıktı**
- Her aday için PDF'te ayrı bir sayfa, üç bölüm hâlinde:
  1. **Parametreler** — kategori, semt, skor, faaliyet durumu, güncellik, teknoloji sinyalleri
  2. **Bilgiler ve iletişim** — adres, telefon, sitede bulunan e-posta, sosyal medya, kanıt linki + **öncelik sıralı iletişim planı** ("1. Telefon: … 2. E-posta: … 3. Yerinde ziyaret: …") + **görüşme açılış cümlesi önerisi** (bulgulardan üretiliyor)
  3. **Web sitesi hata ve sorunları** — doğrulanmış sorunlar kırmızı, sezgisel bulgular ayrı, altında teknik denetim tablosu
- Rapor dosya adı şehir + tarih + saat içeriyor; **hiçbir rapor üzerine yazılmıyor.**
- Ayrıca ham veri JSON olarak da çıkıyor.

**Kullanım**
- Tarayıcıda çalışan **yerel kontrol paneli**: şehir, semt, sektör seçiyorsun, taramayı başlatıyorsun, ilerleme canlı akıyor, bitince PDF bağlantısı çıkıyor. Panel için hiçbir ek bağımlılık kurulmuyor — Python'un yerleşik web sunucusuyla çalışıyor.
- Windows Görev Zamanlayıcı ile **her pazartesi 09:00'da otomatik** çalıştırılabiliyor.
- Çift tıklanabilir `.bat` kısayolları var; komut yazmayı bilmeyen biri de kullanabiliyor.

**İsteğe bağlı zenginleştirme (Firecrawl)**
- Rehberlerden (yelp.de, gelbeseiten.de, jameda.de) **puan ve yorum sayısı** çekiliyor.
- JavaScript ile yüklenen siteler düzgün taranıyor.
- **Kredi verimliliği:** Firecrawl sadece yerel tarama ince/başarısız içerik döndürdüğünde devreye giriyor — her sitede değil. Aday başına ~2 kredi.
- Anahtar depoda **yok**, çalışma anında ortamdan okunuyor — projeyi indiren herkes kendi hesabını kullanıyor.

**Mühendislik / profesyonellik tarafı**
- **MIT lisansı** — açık kaynak, kullanımı serbest.
- **SECURITY.md** — hiçbir API anahtarının depoda tutulmadığı, taranan işletme verisinin yerel kaldığı ve sorumlu kullanım sınırları yazılı.
- **Gizlilik bilinci:** taranan gerçek işletme verileri (`output/`, `data/`) `.gitignore` ile depodan dışlanıyor — üçüncü kişilerin iletişim bilgilerini yayınlamak GDPR/KVKK açısından sorun olurdu.
- **Nazik tarama:** istekler arasında bekleme, site başına tek istek, yalnızca herkese açık veri. Sistem **hiç kimseye otomatik mesaj göndermiyor** — iletişim kararı her zaman insanda.
- İki dilli dokümantasyon (İngilizce + Türkçe README), sistemin çalışma mantığını anlatan ayrı bir **rehber PDF**.

---

## HİKÂYENİN ÇEKİRDEĞİ (gönderinin ruhu bu olmalı)

Bu proje sıfırdan bir fikir değil. Başlangıç noktası, n8n üzerinde kurulmuş bir otomasyon akışıydı: iki GPT ajanı, Firecrawl, Supabase, Gmail ve n8n'in kendisi — **beş ayrı servise bağımlı, her çalıştırmada para yakan** bir kurulum.

Ona bakarken şunu fark ettim: akışın içindeki yapay zekâ talimatlarının neredeyse tamamı aslında **kodla doğrulanabilir nesnel kontrollerdi** — "HTTPS var mı", "viewport etiketi var mı", "iletişim linki çalışıyor mu". Yapay zekâya bunları *sorup* cevabına güvenmek yerine, kodun bunları *ölçmesi* gerekiyordu.

Ben de sistemi baştan yazdım: **yapay zekâ mimariyi kurarken ve kodu yazarken yanımdaydı; ama nihai kararı kod veriyor.** Sonuç: aynı iş mantığı, ama tekrarlanabilir, halüsinasyonsuz, platform bağımsız ve tekrar eden maliyeti sıfır.

> Kısaca: **yapay zekâyı düşünmesi gereken yerde kullandım, doğrulaması gereken yerde koda bıraktım.** Gönderinin ana fikri bu olsun.

---

## GÖNDERİYLE BİRLİKTE PAYLAŞACAĞIM 4 GÖRSEL

Sıra önemli. Gönderi metnini bu akışa uygun kur:
1. **Kapak** — LeadRadar ne yapar, boru hattı ve skorlama özeti
2. **Problem** — ticari problem + gerçek tarama rakamları (Münih %72, Köln %78)
3. **Kontrol paneli** — şehir/semt/sektör seçimi ekranı
4. **Rapor çıktısı** — bir adayın rapor sayfası, tespit edilen gerçek sorunlarla (işletme kimliği gizlenmiş)

---

## YAZIM KURALLARI — BUNLARA UY

**Ton**
- Birinci tekil şahıs, sakin, kendinden emin ama **iddiacı değil**. Abartı sıfat yok.
- Satış kokmayacak. Kimseye bir şey pazarlamıyorum; yaptığım işi anlatıyorum.
- "Devrim", "oyun değiştirici", "inanılmaz", "tutkuyla", "heyecanla paylaşıyorum" gibi kalıpları **kullanma**.
- Emoji: en fazla 2-3 tane, sadece bölüm ayırıcı olarak. Emoji yağmuru yok.
- Hashtag: en fazla 5 tane, sonda, anlamlı olanlar.

**Yapı**
- **İlk iki satır kritik** (LinkedIn gerisini gizliyor). Bir problem cümlesi ya da çarpıcı bir gerçek rakamla aç — proje adıyla değil.
- Toplam uzunluk: **1300-1900 karakter** arası. Uzun tutma.
- Kısa paragraflar, bolca satır boşluğu. Telefonda okunabilir olsun.
- Ortada bir yerde "nasıl çalıştığı"nı 3-4 maddeyle ver, hepsini değil.
- Sonda GitHub linki + yumuşak bir kapanış (soru sormak iyi, yalvarmak kötü).

**Yapay zekâ ile geliştirdiğimi nasıl söyle**
- Savunmacı olma, özür diler gibi olma. "Yapay zekâ ile geliştirdim" bir itiraf değil, bir yetkinlik beyanı.
- Ama şunu da net et: yapay zekâ **her şeyi yapmadı** — mimari kararları, hangi kontrolün nesnel hangisinin öznel olduğu ayrımını, puanlama guardrail'lerini ben kurdum.

**AI-tell'lerden kaçın (bunlar gönderiyi yapay yapar)**
- "— " (em dash) zincirlemesi, "sadece … değil, aynı zamanda …", "X'in gücünü keşfedin"
- Her paragrafın aynı uzunlukta olması
- Üçlü liste saplantısı (her şeyi üç maddeye bölmek)
- "Sonuç olarak", "Özetle" gibi kapanış klişeleri
- Aşırı simetrik cümle yapıları

**Gerçeklik kuralı**
- Verdiğim rakamların dışına çıkma, **yeni istatistik uydurma.** Münih %72 ve Köln %78 gerçek ölçümler; başka rakam ekleme.
- "Şu kadar müşteri buldum", "şu kadar satış yaptım" gibi **olmayan sonuçlar iddia etme.** Bu bir araç; henüz ticari sonuç raporlamıyorum.

---

## ÇIKTI OLARAK BANA ŞUNLARI VER

1. **Gönderi metni** (Türkçe, yayına hazır, kopyalayıp yapıştırabileceğim halde)
2. **2 alternatif açılış cümlesi** (ilk iki satırı test edebilmek için)
3. **Kısa İngilizce sürümü** (~800-1000 karakter)
4. **Hashtag önerisi** (en fazla 5)
5. **Her görsel için tek cümlelik alt yazı** (LinkedIn carousel'de görsel açıklaması olarak kullanacağım)
