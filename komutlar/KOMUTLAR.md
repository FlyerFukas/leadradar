# LeadRadar — Komut Rehberi

Bu klasördeki `.bat` dosyalarına **çift tıklayarak** sistemi komut yazmadan
kullanabilirsin. Aşağıda hem kısayolların ne yaptığı, hem de aynı işi yapan
PowerShell komutları yazılıdır.

---

## Tek tıkla kısayollar (bu klasördeki dosyalar)

| Dosya | Ne yapar |
|---|---|
| **1-Panel-Baslat.bat** | Kontrol panelini açar. Şehir / semt / sektör seçip taramayı başlatırsın. **En çok kullanacağın dosya.** |
| **2-Hizli-Tarama.bat** | Seçim yapmadan, varsayılan Berlin haftalık rotasyonuyla hemen tarama yapar. |
| **3-Ciktilari-Ac.bat** | `output` klasörünü açar (raporların bulunduğu yer). |
| **4-Haftalik-Otomatik-Kur.bat** | Her Pazartesi 09:00'da otomatik tarama kurar. Bir kez çalıştırman yeterli. |
| **5-Otomatigi-Iptal-Et.bat** | Haftalık otomatik görevi kaldırır. |
| **6-Sistem-Rehberi-Olustur.bat** | Sistemin çalışma mantığını anlatan PDF'i yeniden üretir. |
| **7-Kurulum-Gereksinimler.bat** | Gerekli Python paketlerini kurar (sadece ilk kurulumda gerekir). |

---

## Aynı işlerin PowerShell komutları

Önce proje klasörüne geç:

```powershell
cd C:\Users\furka\Music\LeadRadar
```

### Kontrol paneli (önerilen kullanım)

```powershell
py panel.py
```

Tarayıcıda `http://127.0.0.1:8765` açılır. Şehir, semt ve sektörleri seçip
Firecrawl'ı açıp kapatarak taramayı başlatırsın. İlerleme canlı akar, bitince
PDF bağlantısı çıkar. Paneli kapatmak için pencerede `Ctrl+C`.

### Hızlı tarama (panelsiz)

```powershell
py run.py                # varsayılan: Berlin, haftalık rotasyon, 10 aday
py run.py --limit 5      # daha az adayla hızlı deneme
py run.py --week 31      # başka bir haftanın rotasyonunu zorla (test için)
```

### Haftalık otomatik çalıştırma

```powershell
powershell -ExecutionPolicy Bypass -File haftalik_zamanlama.ps1   # kur
schtasks /Query /TN "LeadRadar Lead Avcisi"                          # kontrol et
schtasks /Delete /TN "LeadRadar Lead Avcisi" /F                      # iptal et
```

### Sistem rehberi PDF'i

```powershell
py make_system_guide.py
```

### İlk kurulum (yeni bilgisayarda)

```powershell
py -m pip install -r requirements.txt
```

---

## Çıktılar nereye düşüyor?

Hepsi `C:\Users\furka\Music\LeadRadar` altında:

| Ne | Yer |
|---|---|
| **Lead raporu (PDF)** | `output\LeadRadar_Lead_Raporu_<Şehir>_<tarih>_<saat>.pdf` |
| Ham veri (JSON) | `output\LeadRadar_calistirma_<Şehir>_<tarih>_<saat>.json` |
| Sistem rehberi (PDF) | `docs\LeadRadar_Sistem_Rehberi.pdf` |
| Hafıza (veritabanı) | `data\leads.db` |

Her çalıştırma **ayrı dosya** oluşturur — eski raporlar silinmez.

---

## Sık sorulanlar

**Aynı işletmeler tekrar gelir mi?**
Hayır. `data\leads.db` daha önce raporlanan işletmeleri hatırlar ve eler.
Sıfırdan başlamak istersen bu dosyayı silmen yeterli.

**Firecrawl'ı nasıl kapatırım?**
Panelde "Firecrawl zenginleştirme" kutucuğunu kaldır. Kalıcı olarak kapatmak
için `config.json` içinde `"firecrawl": {"enabled": false}` yap.

**Başka şehir nasıl tararım?**
Panelden şehir seç. Listede yoksa "Şehir (elle)" kutusuna yaz.
Semt kutusunu boş bırakırsan bütün şehir taranır.

**Rapor boş geldi, neden?**
O şehir/semt ve sektörlerde yeni aday kalmamış olabilir (hepsi daha önce
raporlanmış). Farklı sektör/semt seç ya da veritabanını sıfırla.
