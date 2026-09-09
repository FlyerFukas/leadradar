"""Web sitesi denetimi — orijinal 'AI Agent — enrichment' asamasinin
deterministik karsiligi.

Orijinal sistem mesajindaki "nesnel engel" (objective blocker) listesi burada
kodla dogrulanir:
  1. Calismayan/eksik iletisim yolu (telefon, e-posta, iletisim sayfasi yok)
  2. Bozuk rezervasyon/randevu yolu (olu link, 404)
  3. Mobil uyumsuzluk (viewport meta etiketi yok)
  4. HTTPS yok (site http uzerinden sunuluyor / sertifika gecersiz)
  5. Bariz sayfa hatalari (yuklenmiyor, bos sayfa, sunucu hatasi, sonsuz yonlendirme)

Sezgisel (heuristic) bulgular AYRI tutulur ve '[HEURISTIC]' onekiyle isaretlenir;
tek baslarina asla 'High' skoru uretmezler (orijinal guardrail kurali).
"""

import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CONTACT_WORDS = re.compile(r"kontakt|contact|impressum|iletisim|iletişim", re.I)
BOOKING_WORDS = re.compile(
    r"termin|buchen|booking|reserv|tisch|appointment|randevu", re.I
)
BOOKING_PLATFORMS = (
    "doctolib", "opentable", "resmio", "treatwell", "calendly", "quandoo",
    "jameda", "planity", "shore.com", "timify",
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s\-/().]*\d(?:[\s\-/().]*\d){5,}|\b0\d{2,4}[\s\-/.]?\d{3}(?:[\s\-/.]?\d{2,}){1,3})")
COPYRIGHT_RE = re.compile(r"(?:©|&copy;|\bcopyright\b)[^0-9]{0,20}((?:19|20)\d{2})", re.I)


def _headers(cfg):
    return {
        "User-Agent": cfg["user_agent"],
        "Accept-Language": "de,en;q=0.8,tr;q=0.6",
    }


def _try_get(url, cfg, verify=True):
    return requests.get(
        url,
        timeout=cfg["http_timeout"],
        headers=_headers(cfg),
        allow_redirects=True,
        verify=verify,
    )


def _fetch_page(website, cfg, result):
    """Once https, olmazsa http dener; SSL/baglanti sorunlarini kaydeder."""
    raw = website.strip()
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urlparse(raw)
    base = parsed.netloc + parsed.path + (("?" + parsed.query) if parsed.query else "")
    https_url = "https://" + base
    http_url = "http://" + base

    for url, verify in ((https_url, True), (https_url, False), (http_url, True)):
        try:
            resp = _try_get(url, cfg, verify=verify)
            if not verify:
                result["ssl_error"] = True
            return resp
        except requests.exceptions.SSLError:
            result["ssl_error"] = True
            continue
        except requests.exceptions.TooManyRedirects:
            result["redirect_loop"] = True
            return None
        except requests.exceptions.RequestException as exc:
            result.setdefault("fetch_errors", []).append(f"{url}: {type(exc).__name__}")
            continue
    return None


def _clean_emails(candidates):
    bad_ends = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")
    out = []
    for e in candidates:
        low = e.lower()
        if low.endswith(bad_ends) or "example." in low or "@2x" in low:
            continue
        if low not in out:
            out.append(low)
    return out[:5]


def _check_links(links, base_url, cfg, max_check=2):
    """Ayni alan adindaki linklerden en fazla max_check tanesini dogrular."""
    broken, checked = [], 0
    base_host = urlparse(base_url).hostname
    for href in links:
        if checked >= max_check:
            break
        full = urljoin(base_url, href)
        if urlparse(full).hostname != base_host:
            continue  # dis platformlar (Doctolib vb.) burada test edilmez
        checked += 1
        try:
            r = requests.get(full, timeout=cfg["http_timeout"], headers=_headers(cfg), allow_redirects=True)
            if r.status_code >= 400:
                broken.append(f"{full} (HTTP {r.status_code})")
        except requests.exceptions.RequestException as exc:
            broken.append(f"{full} ({type(exc).__name__})")
        time.sleep(0.5)
    return broken


def _fresh_result(website):
    return {
        "input_url": website,
        "final_url": None,
        "http_status": None,
        "loads": False,
        "https": False,
        "ssl_error": False,
        "redirect_loop": False,
        "blank": False,
        "viewport": None,
        "title": None,
        "phones_on_site": [],
        "emails": [],
        "has_mailto": False,
        "contact_links": [],
        "broken_contact_links": [],
        "booking_links": [],
        "external_booking": [],
        "broken_booking_links": [],
        "copyright_year": None,
        "last_modified": None,
        "generator": None,
        "tech_signals": [],
        "social_links": [],
        "objective_issues": [],
        "heuristic_issues": [],
        "blocker_count": 0,
        "firecrawl_used": False,
        "_text_len": 0,
    }


def audit_website(website, cfg, firecrawl_client=None):
    """Tek bir web sitesini denetler; nesnel/sezgisel bulgular dondurur.

    firecrawl_client verilirse, yerel tarama ince/basarisiz oldugunda (JS ile
    yuklenen siteler) Firecrawl ile yeniden denenir ve daha zengin sonuc alinir.
    """
    result = _fresh_result(website)
    resp = _fetch_page(website, cfg, result)

    if resp is not None and resp.status_code < 400:
        result["final_url"] = resp.url
        result["http_status"] = resp.status_code
        result["last_modified"] = resp.headers.get("Last-Modified")
        result["https"] = urlparse(resp.url).scheme == "https"
        result["loads"] = True
        _analyze_html(resp.text[:1_500_000], resp.url, cfg, result)

    # Yerel tarama zayifsa (acilmadi / bos / cok ince icerik) Firecrawl'i dene
    weak = (
        resp is None
        or resp.status_code >= 400
        or result["blank"]
        or result["_text_len"] < 800
    )
    if firecrawl_client is not None and weak:
        data = firecrawl_client.scrape(website)
        if data and data.get("html"):
            meta = data.get("metadata") or {}
            final = meta.get("url") or meta.get("sourceURL") or website
            fc = _fresh_result(website)
            fc["final_url"] = final
            fc["http_status"] = meta.get("statusCode")
            fc["https"] = str(final).lower().startswith("https")
            fc["loads"] = True
            fc["firecrawl_used"] = True
            _analyze_html(data["html"][:1_500_000], final, cfg, fc)
            # Firecrawl daha dolu icerik getirdiyse onu kullan
            if not fc["blank"] and fc["_text_len"] >= result["_text_len"]:
                fc["blocker_count"] = _count_blockers(fc)
                return fc

    # Firecrawl devreye girmediyse yerel sonucu sonlandir
    obj = result["objective_issues"]
    if resp is None:
        if result["redirect_loop"]:
            obj.append("Sonsuz yönlendirme döngüsü — site açılmıyor")
        else:
            obj.append("Site yüklenmiyor (bağlantı/DNS/zaman aşımı hatası)")
        if result["ssl_error"]:
            obj.append("SSL sertifika hatası")
    elif resp.status_code >= 400:
        obj.append(f"Sayfa hatası: HTTP {resp.status_code}")

    result["blocker_count"] = _count_blockers(result)
    return result


def _analyze_html(html, final_url, cfg, result):
    """Ham HTML uzerinden tum nesnel/sezgisel kontrolleri yapar (kaynak: requests
    ya da Firecrawl). result sozlugunu yerinde doldurur."""
    obj = result["objective_issues"]
    heur = result["heuristic_issues"]

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    result["_text_len"] = len(text)

    # --- Bos sayfa ---
    if len(text) < 200:
        result["blank"] = True
        obj.append("Sayfa neredeyse boş — kritik içerik yok")

    # --- HTTPS ---
    if not result["https"]:
        obj.append("HTTPS yok — site şifrelenmemiş http üzerinden sunuluyor")
    elif result["ssl_error"]:
        obj.append("SSL sertifikası geçersiz/hatalı")

    # --- Mobil uyumluluk (viewport) ---
    viewport = soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)})
    result["viewport"] = viewport is not None
    if not result["blank"] and not result["viewport"]:
        obj.append("Mobil uyumlu değil — viewport meta etiketi yok")

    # --- Baslik ---
    if soup.title and soup.title.string:
        result["title"] = soup.title.string.strip()[:150]

    # --- Iletisim yollari ---
    tel_links = [a.get("href", "") for a in soup.find_all("a", href=re.compile(r"^tel:", re.I))]
    phones = [t[4:] for t in tel_links] + PHONE_RE.findall(text[:20000])
    result["phones_on_site"] = list(dict.fromkeys(p.strip() for p in phones))[:3]
    result["has_mailto"] = bool(soup.find("a", href=re.compile(r"^mailto:", re.I)))
    result["emails"] = _clean_emails(EMAIL_RE.findall(html))

    all_links = [(a.get("href", ""), a.get_text(" ", strip=True)) for a in soup.find_all("a", href=True)]
    for href, label in all_links:
        blob = f"{href} {label}"
        low = href.lower()
        if any(s in low for s in ("facebook.com", "instagram.com", "tiktok.com")):
            if href not in result["social_links"]:
                result["social_links"].append(href)
        if CONTACT_WORDS.search(blob) and href not in result["contact_links"]:
            result["contact_links"].append(href)
        if BOOKING_WORDS.search(blob) or any(p in low for p in BOOKING_PLATFORMS):
            if any(p in low for p in BOOKING_PLATFORMS):
                if href not in result["external_booking"]:
                    result["external_booking"].append(href)
            elif href not in result["booking_links"]:
                result["booking_links"].append(href)

    has_contact_path = bool(
        result["phones_on_site"] or result["has_mailto"] or result["emails"]
        or result["contact_links"]
    )
    if not result["blank"] and not has_contact_path:
        obj.append("İletişim yolu yok — sayfada telefon, e-posta veya iletişim linki bulunamadı")
    elif result["contact_links"]:
        result["broken_contact_links"] = _check_links(result["contact_links"], final_url, cfg)
        if result["broken_contact_links"] and not (result["phones_on_site"] or result["emails"]):
            obj.append("İletişim sayfası bozuk: " + "; ".join(result["broken_contact_links"]))

    if result["booking_links"]:
        result["broken_booking_links"] = _check_links(result["booking_links"], final_url, cfg)
        if result["broken_booking_links"]:
            obj.append("Rezervasyon/randevu linki bozuk: " + "; ".join(result["broken_booking_links"]))

    # --- Tazelik ---
    years = [int(y) for y in COPYRIGHT_RE.findall(html)]
    if years:
        result["copyright_year"] = max(years)

    # --- Teknoloji sinyalleri ---
    gen = soup.find("meta", attrs={"name": re.compile("^generator$", re.I)})
    if gen and gen.get("content"):
        result["generator"] = gen["content"].strip()[:80]
        result["tech_signals"].append(result["generator"])
    low_html = html.lower()
    for marker, label in (
        ("wp-content", "WordPress"), ("wix.com", "Wix"), ("jimdo", "Jimdo"),
        ("squarespace", "Squarespace"), ("shopify", "Shopify"),
        ("typo3", "TYPO3"), ("joomla", "Joomla"),
    ):
        if marker in low_html and all(label.lower() not in t.lower() for t in result["tech_signals"]):
            result["tech_signals"].append(label)
    jq = re.search(r"jquery[-.]?(\d+)\.(\d+)", low_html)
    if jq:
        result["tech_signals"].append(f"jQuery {jq.group(1)}.{jq.group(2)}")

    # --- Sezgisel bulgular ([HEURISTIC] onekiyle) ---
    current_year = datetime.now().year
    if result["copyright_year"] and result["copyright_year"] <= current_year - 2:
        heur.append(f"[HEURISTIC] Alt bilgideki telif yılı eski ({result['copyright_year']}) — site uzun süredir güncellenmemiş olabilir")
    if jq and int(jq.group(1)) == 1:
        heur.append(f"[HEURISTIC] Çok eski jQuery {jq.group(1)}.{jq.group(2)} sürümü — bakımsızlık işareti")
    if result["generator"]:
        wp = re.search(r"wordpress\s*(\d+)", result["generator"], re.I)
        if wp and int(wp.group(1)) < 6:
            heur.append(f"[HEURISTIC] Eski CMS sürümü: {result['generator']}")
    if not result["blank"]:
        if not result["title"] or len(result["title"]) < 5:
            heur.append("[HEURISTIC] Sayfa başlığı (title) yok/çok kısa — zayıf SEO")
        if not soup.find("meta", attrs={"name": re.compile("^description$", re.I)}):
            heur.append("[HEURISTIC] Meta açıklama (description) yok — zayıf SEO")
    if ".swf" in low_html:
        heur.append("[HEURISTIC] Flash içeriği tespit edildi — teknoloji çok eski")


def _count_blockers(result):
    """Orijinal guardrail listesindeki 5 nesnel engel kategorisini sayar."""
    obj = result["objective_issues"]
    categories = 0
    if any("yüklenmiyor" in i or "Sayfa hatası" in i or "boş" in i or "yönlendirme" in i for i in obj):
        categories += 1
    if any("HTTPS" in i or "SSL" in i for i in obj):
        categories += 1
    if any("Mobil uyumlu" in i for i in obj):
        categories += 1
    if any("İletişim" in i for i in obj):
        categories += 1
    if any("Rezervasyon" in i for i in obj):
        categories += 1
    return categories
