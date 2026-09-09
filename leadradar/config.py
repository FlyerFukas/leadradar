"""Yapılandırma: varsayılanlar + istege bagli config.json ile ezme (override)."""

import copy
import json
import os

DEFAULTS = {
    # Hedef sehir ve OSM idari seviyeleri (Berlin: sehir=4, semtler=9/10)
    "city": "Berlin",
    "city_admin_levels": "4",
    "district_admin_levels": "9|10",

    # Haftalik hedefler (orijinal akis: 20 kesif -> 10 secim)
    "discover_pool": 20,
    "target_leads": 10,
    # Secilen leadlerin en az bu orani "web sitesi yok" olmali (orijinal: 12/20)
    "no_website_ratio": 0.6,

    # Nazik tarama ayarlari
    "request_delay_sec": 1.5,
    "http_timeout": 20,
    "user_agent": "LeadRadar-LeadScout/1.0 (kisisel arastirma araci)",

    # Haftalik rotasyon (orijinal Rotation Seed dugumuyle birebir ayni listeler)
    "category_rotation": [
        ["Friseur", "Restaurant", "Fitnessstudio"],
        ["Fitnessstudio", "Zahnarzt", "Friseur"],
        ["Restaurant", "Friseur", "Zahnarzt"],
        ["Zahnarzt", "Restaurant", "Fitnessstudio"],
    ],
    "area_rotation": [
        ["Mitte", "Neukölln", "Kreuzberg"],
        ["Charlottenburg", "Wilmersdorf", "Schöneberg"],
        ["Prenzlauer Berg", "Friedrichshain", "Pankow"],
        ["Spandau", "Tempelhof", "Steglitz"],
    ],

    # Kategori (sektor) -> OSM etiket eslemesi. Panel bu listeden secim sunar.
    "category_osm": {
        "Friseur": [["shop", "hairdresser"]],
        "Restaurant": [["amenity", "restaurant"]],
        "Café": [["amenity", "cafe"]],
        "Bäckerei": [["shop", "bakery"]],
        "Fitnessstudio": [["leisure", "fitness_centre"]],
        "Zahnarzt": [["amenity", "dentist"], ["healthcare", "dentist"]],
        "Arzt": [["amenity", "doctors"], ["healthcare", "doctor"]],
        "Apotheke": [["amenity", "pharmacy"]],
        "Kosmetikstudio": [["shop", "beauty"]],
        "Tattoostudio": [["shop", "tattoo"]],
        "Blumenladen": [["shop", "florist"]],
        "Metzgerei": [["shop", "butcher"]],
        "Autowerkstatt": [["shop", "car_repair"]],
        "Immobilienmakler": [["office", "estate_agent"]],
        "Rechtsanwalt": [["office", "lawyer"]],
        "Steuerberater": [["office", "tax_advisor"]],
        "Tierarzt": [["amenity", "veterinary"]],
        "Physiotherapie": [["healthcare", "physiotherapist"]],
        "Hotel": [["tourism", "hotel"]],
        "Bar/Kneipe": [["amenity", "bar"], ["amenity", "pub"]],
        "Eisdiele": [["amenity", "ice_cream"]],
        "Optiker": [["shop", "optician"]],
        "Juwelier": [["shop", "jewelry"]],
        "Bekleidungsgeschäft": [["shop", "clothes"]],
        "Reinigung": [["shop", "dry_cleaning"]],
    },

    # Sektor Turkce etiketleri (panelde gosterim icin; veri Almanca kalir)
    "sector_labels_tr": {
        "Friseur": "Kuaför", "Restaurant": "Restoran", "Café": "Kafe",
        "Bäckerei": "Fırın", "Fitnessstudio": "Spor salonu", "Zahnarzt": "Diş hekimi",
        "Arzt": "Doktor/Muayenehane", "Apotheke": "Eczane", "Kosmetikstudio": "Güzellik salonu",
        "Tattoostudio": "Dövme stüdyosu", "Blumenladen": "Çiçekçi", "Metzgerei": "Kasap",
        "Autowerkstatt": "Oto tamir", "Immobilienmakler": "Emlakçı", "Rechtsanwalt": "Avukat",
        "Steuerberater": "Mali müşavir", "Tierarzt": "Veteriner", "Physiotherapie": "Fizyoterapi",
        "Hotel": "Otel", "Bar/Kneipe": "Bar/Pub", "Eisdiele": "Dondurmacı",
        "Optiker": "Gözlükçü", "Juwelier": "Kuyumcu", "Bekleidungsgeschäft": "Giyim mağazası",
        "Reinigung": "Kuru temizleme",
    },

    # Almanya sehir katalogu -> sehir sinirinin OSM admin_level'i.
    # Sehir-eyaletleri (Stadtstaat) admin_level 4; digerleri (kreisfreie Stadt) 6.
    "city_catalog": {
        "Berlin": "4", "Hamburg": "4", "Bremen": "4",
        "München": "6", "Köln": "6", "Frankfurt am Main": "6", "Stuttgart": "6",
        "Düsseldorf": "6", "Leipzig": "6", "Dortmund": "6", "Essen": "6",
        "Dresden": "6", "Hannover": "6", "Nürnberg": "6", "Duisburg": "6",
        "Bochum": "6", "Wuppertal": "6", "Bonn": "6", "Münster": "6",
        "Karlsruhe": "6", "Mannheim": "6", "Augsburg": "6", "Wiesbaden": "6",
        "Bielefeld": "6", "Mönchengladbach": "6", "Kiel": "6", "Freiburg im Breisgau": "6",
    },

    # Zincir/franchise dislama (orijinal kural: zincirleri disla).
    # OSM "brand" etiketi olan her kayit otomatik dislanir; bu liste ek guvence.
    "chain_blacklist": [
        "mcdonald", "burger king", "kfc", "subway", "domino", "pizza hut",
        "nordsee", "vapiano", "block house", "l'osteria", "hans im glück",
        "dean&david", "dean & david", "backwerk", "starbucks", "starbucks",
        "mcfit", "fitx", "clever fit", "superfit", "super fit", "holmes place",
        "john reed", "fitness first", "kieser",
        "essanelle", "klier", "ryf", "cut & go", "cut&go", "cut and go", "hairexpress",
    ],

    # Overpass API uclari (ilki calismezsa sonrakiler denenir)
    "overpass_endpoints": [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ],
    "overpass_limit": 80,

    # Istege bagli yapay zeka cilasi (why_lead / sezgisel degerlendirme metinleri)
    "ai": {
        "enabled": False,
        "provider": "anthropic",   # "anthropic" veya "openai"
        "model": None,              # None -> saglayicinin varsayilani
    },

    # Istege bagli Firecrawl zenginlestirmesi (anahtar: FIRECRAWL_API_KEY veya CLI login)
    "firecrawl": {
        "enabled": False,          # True -> puan/yorum + guclu tarama devreye girer
        "enrich_ratings": True,    # rehberlerden public_rating / review_count cek
        "scrape_sites": True,      # JS'li/ince siteleri Firecrawl ile tara
    },
}


def _deep_merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def load_config(path=None):
    """Varsayilan yapilandirmayi yukler, varsa config.json ile birlestirir."""
    cfg = copy.deepcopy(DEFAULTS)
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            _deep_merge(cfg, json.load(f))
    return cfg
