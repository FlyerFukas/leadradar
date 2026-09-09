"""Kesif asamasi — orijinal 'AI Agent — Discover Fresh' + Firecrawl /search yerine
OpenStreetMap Overpass API ile deterministik isletme kesfi.

Neden Overpass? Ucretsiz, anahtarsiz, yasal olarak sorunsuz ve yapisal veri verir:
isletme adi, adres, telefon, web sitesi (varsa) ve kanit linki (OSM kaydi).
"Web sitesi kaydi yok" sinyali, orijinal akistaki "rehberde site listelenmemis"
sinyalinin karsiligidir.
"""

import re
import time

import requests

from .fingerprint import host, make_fingerprint

SOCIAL_HOSTS = (
    "facebook.com", "m.facebook.com", "instagram.com", "tiktok.com",
    "linktr.ee", "wa.me", "whatsapp.com",
)


def _tag_lines(cfg, categories, area_ref):
    lines = []
    for cat in categories:
        for key, value in cfg["category_osm"][cat]:
            lines.append(f'  nwr["{key}"="{value}"]["name"](area.{area_ref});')
    return "\n".join(lines)


def _build_query(cfg, district, categories):
    """Belirli bir semt (Stadtteil) icindeki isletmeleri sorgular."""
    body = _tag_lines(cfg, categories, "d")
    return f"""[out:json][timeout:120];
area["name"="{cfg['city']}"]["boundary"="administrative"]["admin_level"~"^({cfg['city_admin_levels']})$"]->.city;
rel(area.city)["boundary"="administrative"]["admin_level"~"^({cfg['district_admin_levels']})$"]["name"="{district}"];
map_to_area ->.d;
(
{body}
);
out center tags {cfg['overpass_limit']};"""


def _build_city_query(cfg, categories, city, admin_level, limit):
    """Tum sehir sinirlari icindeki isletmeleri tek sorguda ceker."""
    body = _tag_lines(cfg, categories, "c")
    return f"""[out:json][timeout:150];
area["name"="{city}"]["boundary"="administrative"]["admin_level"~"^({admin_level})$"]->.c;
(
{body}
);
out center tags {limit};"""


def _fetch_overpass(cfg, query, log):
    last_err = None
    for endpoint in cfg["overpass_endpoints"]:
        for attempt in range(2):
            try:
                resp = requests.post(
                    endpoint,
                    data={"data": query},
                    timeout=150,
                    headers={"User-Agent": cfg["user_agent"]},
                )
                if resp.status_code in (429, 504):
                    log(f"    Overpass mesgul ({resp.status_code}), bekleniyor...")
                    time.sleep(20)
                    continue
                resp.raise_for_status()
                return resp.json().get("elements", [])
            except Exception as exc:  # noqa: BLE001 - kesif tek denemede olmemeli
                last_err = exc
                log(f"    Overpass hatasi ({endpoint}): {exc}")
                time.sleep(5)
    raise RuntimeError(f"Overpass sorgusu basarisiz: {last_err}")


def _category_of(tags, cfg, categories):
    for cat in categories:
        for key, value in cfg["category_osm"][cat]:
            if tags.get(key) == value:
                return cat
    return None


def _address_of(tags, district, city):
    street = tags.get("addr:street")
    number = tags.get("addr:housenumber", "")
    postcode = tags.get("addr:postcode", "")
    town = tags.get("addr:city") or city
    if not street:
        return None
    left = f"{street} {number}".strip()
    right = f"{postcode} {town}".strip()
    suffix = f" ({district})" if district and district not in right else ""
    return f"{left}, {right}{suffix}"


def _website_of(tags):
    for key in ("website", "contact:website", "url"):
        if tags.get(key):
            return tags[key].strip().split(";")[0].strip()
    for key in ("contact:facebook", "contact:instagram"):
        if tags.get(key):
            return tags[key].strip()
    return None


def website_tier(website):
    """Secim onceligi: none (site yok) > social (yalniz sosyal medya) >
    http (guvensiz) > has (normal site)."""
    if not website:
        return "none"
    h = host(website)
    if any(h == s or h.endswith("." + s) for s in SOCIAL_HOSTS):
        return "social"
    if website.lower().startswith("http://"):
        return "http"
    return "has"


def _is_chain(tags, name, cfg):
    if tags.get("brand") or tags.get("brand:wikidata"):
        return True
    low = name.lower()
    return any(b in low for b in cfg["chain_blacklist"])


def _element_to_lead(el, district, cfg, categories):
    tags = el.get("tags", {})
    name = (tags.get("name") or "").strip()
    if not name or _is_chain(tags, name, cfg):
        return None
    category = _category_of(tags, cfg, categories)
    if not category:
        return None
    website = _website_of(tags)
    lead = {
        "business_name": name,
        "category": category,
        "district": district,
        "address": _address_of(tags, district, cfg["city"]),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "website": website,
        "website_tier": website_tier(website),
        "source_links": f"https://www.openstreetmap.org/{el['type']}/{el['id']}",
        "services_listed": tags.get("cuisine") or tags.get("healthcare:speciality"),
        "osm_check_date": tags.get("check_date") or tags.get("survey:date"),
        "opening_hours": tags.get("opening_hours"),
    }
    lead["fingerprint"] = make_fingerprint(lead)
    return lead


def _collect(elements, area_label, cfg, categories, leads, seen_fp):
    added = 0
    for el in elements:
        lead = _element_to_lead(el, area_label, cfg, categories)
        if not lead or not lead["fingerprint"]:
            continue
        if lead["fingerprint"] in seen_fp:
            continue
        seen_fp.add(lead["fingerprint"])
        leads.append(lead)
        added += 1
    return added


def discover(cfg, rotation, log=print):
    """Rotasyona gore Overpass sorgusu calistirir, adaylari toplar.

    rotation['whole_city'] True ise sehrin tamami tek sorguda taranir;
    aksi halde rotation['areas'] icindeki her semt ayri ayri taranir.
    """
    leads, seen_fp = [], set()
    categories = rotation["categories"]

    if rotation.get("whole_city"):
        city = rotation.get("city", cfg["city"])
        admin = rotation.get("admin_level", cfg["city_admin_levels"])
        limit = max(cfg["overpass_limit"], 200)
        log(f"  Tüm şehir taranıyor: {city} (admin_level {admin}) ...")
        query = _build_city_query(cfg, categories, city, admin, limit)
        try:
            elements = _fetch_overpass(cfg, query, log)
            added = _collect(elements, city, cfg, categories, leads, seen_fp)
            log(f"    {added} aday bulundu (toplam ham kayit: {len(elements)})")
        except RuntimeError as exc:
            log(f"    Şehir taraması başarısız: {exc}")
        return leads

    for district in rotation["areas"]:
        log(f"  Semt taraniyor: {district} ...")
        query = _build_query(cfg, district, categories)
        try:
            elements = _fetch_overpass(cfg, query, log)
        except RuntimeError as exc:
            log(f"    {district} atlandi: {exc}")
            continue
        added = _collect(elements, district, cfg, categories, leads, seen_fp)
        log(f"    {added} aday bulundu (toplam ham kayit: {len(elements)})")
        time.sleep(2)  # Overpass'a nazik davran
    return leads


def _completeness(lead):
    return sum(bool(lead.get(k)) for k in ("address", "phone", "website"))


def _order_tier(tier_leads):
    """Katman ici siralama: once bilgi butunlugu, kategori/semt cesitliligi
    round-robin ile korunur."""
    bucket_map = {}
    for lead in sorted(tier_leads, key=lambda l: (-_completeness(l), l["business_name"])):
        bucket_map.setdefault((lead["category"], lead["district"]), []).append(lead)
    buckets = list(bucket_map.values())
    ordered = []
    while any(buckets):
        for bucket in buckets:
            if bucket:
                ordered.append(bucket.pop(0))
        buckets = [b for b in buckets if b]
    return ordered


def prioritize(leads, cfg):
    """Orijinal kesif kotasi (12/20): havuzun ~%60'i web sitesi olmayanlardan,
    kalani siteli adaylardan (once zayif web varligi: sosyal/http) doldurulur.
    Boylece denetlenecek siteli adaylar havuzdan hic dusmez."""
    tiers = {"none": [], "social": [], "http": [], "has": []}
    for lead in leads:
        tiers[lead["website_tier"]].append(lead)

    none_ordered = _order_tier(tiers["none"])
    site_ordered = (
        _order_tier(tiers["social"]) + _order_tier(tiers["http"]) + _order_tier(tiers["has"])
    )

    pool_size = cfg["discover_pool"]
    want_none = round(pool_size * cfg["no_website_ratio"])
    pool = none_ordered[:want_none] + site_ordered[: pool_size - want_none]
    if len(pool) < pool_size:  # bir taraf eksikse digerinden tamamla
        leftovers = none_ordered[want_none:] + site_ordered[pool_size - want_none:]
        pool += leftovers[: pool_size - len(pool)]
    return pool


def select_final(unseen_leads, cfg):
    """Nihai secim: hedefin ~%60'i 'web sitesi yok', kalani web sitesi olan
    (once zayif varlik) adaylardan. Orijinal 12/20 hedefinin karsiligi."""
    limit = cfg["target_leads"]
    want_none = round(limit * cfg["no_website_ratio"])

    none_leads = [l for l in unseen_leads if l["website_tier"] == "none"]
    with_site = [l for l in unseen_leads if l["website_tier"] != "none"]

    selected = none_leads[:want_none]
    selected += with_site[: limit - len(selected)]
    if len(selected) < limit:  # bir taraf eksikse digerinden tamamla
        remaining = [l for l in unseen_leads if l not in selected]
        selected += remaining[: limit - len(selected)]
    return selected[:limit]
