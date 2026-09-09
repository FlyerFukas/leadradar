"""Firecrawl istemcisi — istege bagli zenginlestirme katmani.

Orijinal n8n akisindaki Firecrawl /search + /scrape araclarinin karsiligi.
Bu sistemde iki yerde kullanilir (yalniz anahtar varsa ve config'de aciksa):
  1. Puan/yorum zenginlestirme: yelp.de/gelbeseiten.de gibi rehberleri tarayip
     public_rating ve review_count alanlarini doldurur.
  2. Guclu site tarama: JavaScript ile yuklenen siteleri de okur (yerel basit
     tarayici az icerik gordugunde devreye girer).

Anahtar bulma sirasi:
  1. Ortam degiskeni FIRECRAWL_API_KEY
  2. Firecrawl CLI'nin sakladigi kimlik dosyasi (%APPDATA%\\firecrawl-cli\\credentials.json)
Anahtar hicbir yerde bulunamazsa istemci "kapali" olur; sistem Firecrawl'siz calisir.
"""

import json
import os
import re
import time

import requests

_CRED_PATHS = [
    os.path.join(os.environ.get("APPDATA", ""), "firecrawl-cli", "credentials.json"),
    os.path.join(os.environ.get("USERPROFILE", ""), ".firecrawl", "credentials.json"),
    os.path.join(os.environ.get("HOME", ""), ".config", "firecrawl", "credentials.json"),
]


def find_api_key():
    """Ortam degiskeni -> CLI kimlik dosyasi sirasiyla anahtari arar."""
    key = os.environ.get("FIRECRAWL_API_KEY")
    if key:
        return key.strip()
    for path in _CRED_PATHS:
        if path and os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("apiKey"):
                    return data["apiKey"].strip()
            except Exception:
                continue
    return None


class FirecrawlClient:
    BASE = "https://api.firecrawl.dev/v2"

    def __init__(self, api_key, timeout=60):
        self.api_key = api_key
        self.timeout = timeout
        self.credits_used = 0

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def search(self, query, limit=3, sources=("web",)):
        """Web'de arama yapar; sonuc listesi dondurur ([] hata durumunda)."""
        try:
            resp = requests.post(
                f"{self.BASE}/search",
                headers=self.headers,
                json={"query": query[:500], "limit": limit, "sources": list(sources)},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            body = resp.json()
            self.credits_used += body.get("creditsUsed", 0) or 0
            return (body.get("data") or {}).get("web") or []
        except Exception:
            return []

    def scrape(self, url, formats=("markdown", "html", "links"), wait_for=1500):
        """Tek URL'yi tarar; {markdown, html, links, metadata} dondurur (None hata)."""
        try:
            resp = requests.post(
                f"{self.BASE}/scrape",
                headers=self.headers,
                json={
                    "url": url,
                    "formats": list(formats),
                    "onlyMainContent": False,
                    "waitFor": wait_for,
                    "blockAds": True,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            body = resp.json()
            self.credits_used += body.get("creditsUsed", 0) or 0
            return body.get("data") or None
        except Exception:
            return None


def maybe_client(cfg, log=print):
    """config.firecrawl.enabled True ve anahtar bulunuyorsa istemci dondurur."""
    fc = cfg.get("firecrawl", {})
    if not fc.get("enabled"):
        return None
    key = find_api_key()
    if not key:
        log("      Firecrawl acik ama anahtar bulunamadi (FIRECRAWL_API_KEY veya CLI login); atlaniyor.")
        return None
    log("      Firecrawl etkin — puan/yorum ve guclu tarama zenginlestirmesi acik.")
    return FirecrawlClient(key, timeout=cfg.get("http_timeout", 20) * 3)


# ---- Puan / yorum cikarimi (Almanca rehber sayfalarindan, best-effort) ----

_RATING_RE = re.compile(
    r"(\d(?:[.,]\d)?)\s*(?:/\s*5|von\s*5|Sterne|stars|out of 5)", re.I
)
_REVIEW_RE = re.compile(
    r"(\d[\d.\s]*)\s*(?:Bewertung(?:en)?|Rezension(?:en)?|reviews?|yorum)", re.I
)
_DIRECTORY_HOSTS = ("yelp.de", "yelp.com", "gelbeseiten.de", "dasoertliche.de",
                    "golocal.de", "11880.com", "jameda.de")


def enrich_rating(client, lead, cfg, log=print):
    """Isletme icin rehber sayfasi arayip puan/yorum sayisini cikarmaya calisir.

    Dondurur: {'public_rating': str|None, 'review_count': str|None,
               'rating_source': url|None}  (bulunamazsa None degerler).
    """
    name = lead.get("business_name", "")
    district = lead.get("district", "")
    query = f'{name} {district} Berlin Bewertungen'
    results = client.search(query, limit=5)

    # Rehber alan adlarindaki ilk sonucu tercih et
    target = None
    for r in results:
        url = (r.get("url") or "").lower()
        if any(h in url for h in _DIRECTORY_HOSTS):
            target = r
            break
    if not target and results:
        target = results[0]  # rehber yoksa ilk sonucu dene
    if not target:
        return {"public_rating": None, "review_count": None, "rating_source": None}

    # Once arama sonucundaki markdown/aciklama, sonra gerekirse sayfayi tara
    text = (target.get("markdown") or "") + " " + (target.get("description") or "")
    rating = _extract_rating(text)
    reviews = _extract_reviews(text)

    if (rating is None or reviews is None) and target.get("url"):
        scraped = client.scrape(target["url"], formats=("markdown",), wait_for=1200)
        if scraped and scraped.get("markdown"):
            md = scraped["markdown"][:20000]
            rating = rating or _extract_rating(md)
            reviews = reviews or _extract_reviews(md)
        time.sleep(0.5)

    return {
        "public_rating": rating,
        "review_count": reviews,
        "rating_source": target.get("url") if (rating or reviews) else None,
    }


def _extract_rating(text):
    m = _RATING_RE.search(text or "")
    if not m:
        return None
    val = m.group(1).replace(",", ".")
    try:
        f = float(val)
        return str(f) if 0 < f <= 5 else None
    except ValueError:
        return None


def _extract_reviews(text):
    m = _REVIEW_RE.search(text or "")
    if not m:
        return None
    digits = re.sub(r"[^\d]", "", m.group(1))
    return digits or None
