"""Haftalik rotasyon — orijinal 'Rotation Seed' dugumunun birebir uyarlamasi.

Orijinal JavaScript formulu:
    week = ceil(((now - 1 Ocak) / 86400000 + 1 Ocak'in gunu + 1) / 7)
    kategori = category_rotation[week % 4]
    semtler  = area_rotation[week % 4]
"""

import math
from datetime import datetime


def compute_rotation(cfg, now=None, week_override=None):
    now = now or datetime.now()
    if week_override is not None:
        week = week_override
    else:
        jan1 = datetime(now.year, 1, 1)
        days_float = (now - jan1).total_seconds() / 86400.0
        # JS getDay(): Pazar=0 ... Cumartesi=6; Python weekday(): Pazartesi=0
        js_getday = (jan1.weekday() + 1) % 7
        week = math.ceil((days_float + js_getday + 1) / 7)

    categories = cfg["category_rotation"][week % len(cfg["category_rotation"])]
    areas = cfg["area_rotation"][week % len(cfg["area_rotation"])]
    return {
        "week_number": week,
        "categories": list(categories),
        "areas": list(areas),
        "hint": (
            f"Bu hafta odak: kategoriler={', '.join(categories)}; "
            f"semtler={', '.join(areas)}"
        ),
    }
