"""Parmak izi (dedup anahtari) — orijinal 'Compute Fingerprint' dugumunun birebir uyarlamasi.

Oncelik sirasi: isim|adres -> isim|telefon -> isim|site-alan-adi -> isim|
"""

from urllib.parse import urlparse


def norm(s):
    """kucuk harf, bosluk sadelestirme, harf/rakam/bosluk disindakileri silme."""
    if s is None:
        return ""
    s = str(s).lower()
    s = " ".join(s.split())
    return "".join(ch for ch in s if ch.isalnum() or ch.isspace()).strip()


def host(url):
    try:
        if not url:
            return ""
        parsed = urlparse(url if "://" in url else "https://" + url)
        return (parsed.hostname or "").removeprefix("www.").lower()
    except Exception:
        return ""


def make_fingerprint(lead):
    name = norm(lead.get("business_name"))
    addr = norm(lead.get("address"))
    phone = norm(lead.get("phone"))
    whost = host(lead.get("website"))

    if name and addr:
        return f"{name}|{addr}"
    if name and phone:
        return f"{name}|{phone}"
    if name and whost:
        return f"{name}|{whost}"
    return f"{name}|" if name else None
