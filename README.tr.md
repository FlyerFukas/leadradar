# LeadRadar (Turkce)

![LeadRadar — yerel işletme lead keşif sistemi](docs/cover.png)

> English version: [README.md](README.md)

**Yerel işletme lead keşif ve zenginleştirme sistemi.** Bir şehir ve sektör seçersin;
sistem o bölgedeki **web sitesi olmayan ya da sitesi sorunlu** işletmeleri bulur,
kanıta dayalı puanlar ve satış görüşmesine hazır bir **PDF raporu** üretir.

> *Local business lead discovery & enrichment. Pick a city and sectors LeadRadar finds
> businesses with missing or broken websites, scores the opportunity from verifiable
> evidence, and produces a sales-ready PDF report.*

Web tasarımcıları, dijital ajanslar ve yerel B2B satış ekipleri için tasarlandı.

---

## Kontrol paneli

Şehir, isteğe bağlı semtler ve dilediğin kadar sektör seç taramayı başlat,
ilerleme tarayıcıda canlı aksın.

![LeadRadar kontrol paneli](docs/panel.png)

---

## Ne yapar?

- 🗺️ **Keşif** OpenStreetMap (Overpass API) üzerinden 27 Alman şehri ve 25 sektörde
  işletme tarar. API anahtarı gerekmez, ücretsizdir.
- 🔍 **Site denetimi** Her adayın sitesini test eder: HTTPS var mı, mobil uyumlu mu,
  iletişim yolu çalışıyor mu, randevu linki kırık mı, sayfa açılıyor mu.
- 🎯 **Kanıta dayalı puanlama** YÜKSEK / ORTA / DÜŞÜK fırsat skoru. Skor yalnızca
  **doğrulanmış** bulgulardan üretilir; "eski görünüyor" gibi sezgisel izlenimler ayrı
  tutulur ve tek başına asla YÜKSEK skor üretemez.
- 🧠 **Tekilleştirme** Daha önce raporlanan işletmeler bir daha gelmez (SQLite hafıza).
- 📄 **PDF rapor** Her aday için: parametreler → iletişim bilgileri ve iletişim planı →
  web sitesi hataları ve teknik denetim tablosu.
- 🖥️ **Yerel kontrol paneli** Tarayıcıdan şehir/semt/sektör seçip taramayı başlatırsın.

---

## Hızlı başlangıç

```bash
git clone https://github.com/mrFurkan33333/leadradar.git
cd leadradar
py -m pip install -r requirements.txt
py panel.py
```

Tarayıcı otomatik açılır: **http://127.0.0.1:8765** şehir, semt ve sektörleri seç,
"Taramayı Başlat"a bas. İlerleme canlı akar, bitince PDF bağlantısı çıkar.

Panelsiz, komut satırından:

```bash
py run.py                # varsayılan haftalık rotasyon
py run.py --limit 5      # az adayla hızlı deneme
```

**Gereksinim:** Python 3.10+ ve internet bağlantısı.

---

## 🔑 Firecrawl (isteğe bağlı) — kendi hesabını bağlaman gerekir

LeadRadar **Firecrawl olmadan da tam çalışır.** Firecrawl açıkken iki ek yetenek gelir:

1. Rehberlerden (yelp.de, gelbeseiten.de, jameda.de…) **puan ve yorum sayısı** çekme
2. JavaScript ile yüklenen siteleri **düzgün tarama**

**Önemli:** Bu depoda hiçbir API anahtarı yoktur. Sistem anahtarı çalışma anında
senin makinenden okur — yani bu projeyi indiren herkes **kendi Firecrawl hesabını**
kullanır, kendi kredisini harcar. Başkasının kredisi kullanılmaz.

Anahtar iki yerden okunur (sırasıyla):

```bash
# 1) Ortam değişkeni
setx FIRECRAWL_API_KEY "fc-senin-anahtarin"        # Windows
export FIRECRAWL_API_KEY="fc-senin-anahtarin"      # macOS / Linux

# 2) Veya Firecrawl CLI ile giriş yap sistem oradan otomatik okur
npm install -g firecrawl-cli && firecrawl login
```

Anahtar bulunamazsa sistem uyarı verip Firecrawl'sız devam eder. Kapatmak için
`config.json` → `"firecrawl": { "enabled": false }`.

Ücretsiz Firecrawl planı bu iş için fazlasıyla yeterlidir (~2 kredi/aday).

---

## Yapılandırma (`config.json`)

| Ayar | Açıklama |
|---|---|
| `city` | Hedef şehir (varsayılan Berlin) |
| `target_leads` / `discover_pool` | Rapora seçilecek aday sayısı / keşif havuzu |
| `no_website_ratio` | "Web sitesi yok" kotası (0.6 = %60) |
| `category_rotation` / `area_rotation` | Haftalık rotasyon listeleri |
| `category_osm` | Sektör → OpenStreetMap etiket eşlemesi (yeni sektör buradan eklenir) |
| `chain_blacklist` | Zincir/franchise filtresi |
| `firecrawl.enabled` | Firecrawl zenginleştirmesi aç/kapa |
| `ai.enabled` | İsteğe bağlı LLM metin cilası (OpenAI / Anthropic) |

---

## Nasıl çalışır?

```
Rotasyon veya panel seçimi
   ↓
Keşif (OpenStreetMap Overpass)
   ↓
Parmak izi + tekilleştirme (SQLite)
   ↓
Seçim (önce sitesi olmayanlar)
   ↓
Web sitesi denetimi (HTTPS · mobil · iletişim · kırık link · hata)
   ↓
Puanlama (YÜKSEK / ORTA / DÜŞÜK yalnızca kanıtla)
   ↓
Kayıt + PDF raporu
```

Ayrıntılı çalışma mantığı için: `docs/LeadRadar_Sistem_Rehberi.pdf`
(yeniden üretmek için `py make_system_guide.py`).

---

## Komutlar

`komutlar/` klasöründeki `.bat` dosyalarına çift tıklayarak da kullanabilirsin
(panel başlat, hızlı tarama, haftalık otomatik kurulum, çıktıları aç).
Tüm komutların listesi: [`komutlar/KOMUTLAR.md`](komutlar/KOMUTLAR.md)

Haftalık otomatik çalıştırma (Windows, her Pazartesi 09:00):

```powershell
powershell -ExecutionPolicy Bypass -File haftalik_zamanlama.ps1
```

---

## Çıktılar

| Ne | Yer |
|---|---|
| Lead raporu (PDF) | `output/LeadRadar_Lead_Raporu_<Şehir>_<tarih>_<saat>.pdf` |
| Ham veri (JSON) | `output/LeadRadar_calistirma_<Şehir>_<tarih>_<saat>.json` |
| Sistem rehberi (PDF) | `docs/LeadRadar_Sistem_Rehberi.pdf` |
| Hafıza (SQLite) | `data/leads.db` |

Her çalıştırma **ayrı dosya** üretir; eski raporlar silinmez.
`output/` ve `data/` klasörleri gerçek işletme verisi içerdiği için **depoya dahil
edilmez** (`.gitignore`).

---

## Veri kaynakları ve etik

- İşletme verisi: [OpenStreetMap](https://www.openstreetmap.org/copyright) (ODbL)
- Site denetimi: işletmenin kendi herkese açık web sitesi
- Nazik tarama: istekler arasında bekleme, tek seferlik sayfa isteği
- Sistem hiçbir yere otomatik mesaj göndermez — iletişim kararı her zaman kullanıcıya aittir
- Yalnızca herkese açık işletme bilgileri kullanılır

---

## Kökeni

Bu proje, n8n üzerindeki *"Local Business Lead Discovery and Enrichment Agent"*
(Marco's Lead Scout) iş akışının mantığından yola çıkar; ancak n8n, OpenAI ajanları ve
harici veritabanı bağımlılıkları olmadan, bağımsız ve deterministik bir Python
uygulaması olarak sıfırdan yazılmıştır. Orijinaldeki "guardrail" puanlama kuralları
koda dökülmüş, böylece sonuçlar tekrarlanabilir ve halüsinasyonsuz hale gelmiştir.

## Lisans

LeadRadar **açık kaynak değil, kaynağı açık (source-available)** bir projedir.
Çift lisanslıdır:

- **Ticari olmayan kullanım ücretsizdir** —
  [PolyForm Noncommercial 1.0.0](LICENSE). Kişisel öğrenme, hobi projesi,
  araştırma, eğitim kurumları, kamu ve hayır kurumları kapsamdadır; izin
  almanıza gerek yoktur.
- **Ticari kullanım ayrı ve ücretli lisans gerektirir.** LeadRadar'ı bir
  işletme adına müşteri adayı bulmak, nitelemek veya bu adaylarla iletişime
  geçmek için kullanmak ticari kullanımdır. Koşullar, lisans biçimleri ve
  iletişim: **[COMMERCIAL.md](COMMERCIAL.md)**.

Hangi tarafta olduğunuzdan emin değilseniz
[issue açın](https://github.com/FlyerFukas/leadradar/issues) ya da
furkanakduman3452@gmail.com adresine yazın. Cevap vermek ücretsiz ve hızlıdır.

> 9–18 Eylül 2026 arasında yayımlanan sürümler MIT lisanslıydı. MIT geri
> alınamaz; o izin **yalnızca o sürümler için** geçerlidir, sonraki sürümleri
> kapsamaz. Ayrıntı: [COMMERCIAL.md](COMMERCIAL.md) §8.

Katkılar [CONTRIBUTING.md](CONTRIBUTING.md) koşullarıyla kabul edilir; çift
lisans modeli bunu zorunlu kılıyor.

**Veri hakkında:** işletme kayıtları
[OpenStreetMap](https://www.openstreetmap.org/copyright) kaynaklıdır ve ODbL
ile lisanslıdır. Türetilmiş veriyi yeniden dağıtıyorsanız ODbL'nin atıf ve
paylaşım koşulları yukarıdaki lisanstan bağımsız olarak sizi bağlar.
