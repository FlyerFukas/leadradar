# LeadRadar — Oturum Günlüğü ve Devir Notu

> En yeni günlük en üstte. Oturuma başlarken yalnızca en üstteki günlüğü ve
> alttaki **Kalıcı Özet** bölümünü okumak yeterlidir.

---

## 08.10.2026 — Ham veri ambarı, araştırma çerçevesi, font düzeltmesi

**İstem:** Panel çalıştığında taranan verinin tamamı ayrı dosyada verilsin;
sistemin genel olarak ne yaptığı ve veri ambarıyla neler yapılabileceği
belgelensin; danışman hoca için literatür taraması başlıkları çıkarılsın.

**Yapılanlar**

1. **Ham veri ambarı eklendi.** Her çalıştırma artık rapora ek olarak taranan
   her OSM kaydını ayrı dosyalara yazıyor:
   - `output/LeadRadar_TarananVeri_<Şehir>_<tarih>_<saat>.csv` (Excel uyumlu,
     `utf-8-sig`, `;` ayracı)
   - `output/LeadRadar_TarananVeri_<Şehir>_<tarih>_<saat>.json` (ham etiketler dahil)
2. **Koordinatlar artık saklanıyor.** `_coords()` eklendi; node için `lat/lon`,
   way/relation için `center`. Önceden Overpass `out center` ile geliyordu ama
   atılıyordu. Mekânsal analiz için kritikti.
3. **Eleme defteri.** `_element_to_lead` artık `(lead, kayit)` döndürüyor;
   elenen kayıtlar sebebiyle birlikte saklanıyor. Eleme sebepleri:
   `isim_etiketi_yok`, `zincir_marka_etiketi`, `zincir_kara_liste`,
   `secili_kategori_disi`, `parmak_izi_uretilemedi`, `ayni_taramada_mukerrer`,
   `onceki_haftalarda_raporlandi`, `havuzda_kaldi_rapora_girmedi`,
   `havuz_disinda_kaldi`. Aşamalar: `ham_kayit`, `cerceveye_girdi`,
   `oncelik_havuzunda`, `rapora_secildi`, `elendi`.
4. **`discover()` imzası değişti:** artık `(leads, defter)` döndürüyor.
   Tek çağrı yeri `run.py:107`.
5. **Araştırma Çerçevesi belgesi** üretildi (`make_arastirma_pdf.py` →
   `docs/LeadRadar_Arastirma_Cercevesi.pdf`, 6 sayfa): sistemin genel
   konumlandırması, Yemeksepeti/Google Maps/Yelp karşılaştırması
   (talep tarafı ile arz tarafı ayrımı), veri ambarının içeriği, 6 başlıkta
   araştırma soruları, **A'dan G'ye literatür başlık haritası**, 4 olası
   makale çerçevesi.
6. **Font ailesi hatası düzeltildi.** `report.py` içinde `registerFontFamily`
   çağrılmıyordu; bu yüzden **tüm PDF'lerde `<b>` ve `<i>` sessizce etkisizdi**
   ve vurgular kayboluyordu. Dört kesim (düz, kalın, italik, kalın-italik)
   kaydedilip aile bağlandı. Üç belge de yeniden üretildi.

**Doğrulama**
- Bonn / kuaför: 200 ham kayıt, 200/200 koordinat, dağılım 176+17+2+3+2 = 200 ✓
- Leipzig / diş hekimi: 168 ham kayıt, dağılım 147+18+1+2 = 168 ✓
- PDF font denetimi: `SegoeUI`, `SegoeUI-Bold`, `SegoeUI-Italic` üçü de kullanımda ✓

**Açık kalan**
- Haftalık otomatik görev (`haftalik_zamanlama.ps1`) hâlâ kurulmadı.
- Gemini entegrasyonu (`ai_polish.py`) hâlâ eklenmedi; OpenAI ve Anthropic var.
- Panel arayüzü ham veri dosyalarına bağlantı göstermiyor; şu an yalnızca PDF
  bağlantısı var.

---

## Kalıcı Özet

**Ne:** Yerel işletme lead keşif ve zenginleştirme sistemi. Açık coğrafi veriden
(OpenStreetMap / Overpass) işletme çeker, web sitelerini fiilen denetler,
kanıta dayalı puanlar, PDF rapor üretir.

**Çalıştırma**
```
py panel.py        # yerel panel, http://127.0.0.1:8765
py run.py          # komut satırı, haftalık rotasyon
py run.py --limit 5
```

**Belgeler** (`docs/`)
| Dosya | İçerik |
|---|---|
| `LeadRadar_Sistem_Rehberi.pdf` | Sistem nasıl çalışır, uçtan uca |
| `LeadRadar_Teorik_Cerceve.pdf` | Yöntem, örnekleme, yanlılık (akademik) |
| `LeadRadar_Arastirma_Cercevesi.pdf` | Konumlandırma, veri ambarı, literatür haritası |

Üretmek için: `py make_system_guide.py`, `py make_teori_pdf.py`,
`py make_arastirma_pdf.py`

**Lisans:** PolyForm Noncommercial 1.0.0 + ayrı ticari lisans. Kaynağı açık,
**açık kaynak değil**. Ayrıntı `COMMERCIAL.md`. MIT dönemi 9-18 Eylül 2026
arasıydı, geri alınamaz; `mit-son` ve `v1.0-polyform` etiketleriyle sınır
kayıtlı.

**Gizlilik:** `output/` ve `data/` gerçek işletme iletişim verisi içerir,
`.gitignore` ile depo dışındadır. Depoya asla eklenmemeli.

**Depo:** github.com/FlyerFukas/leadradar (public)
