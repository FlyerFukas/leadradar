# -*- coding: utf-8 -*-
# LeadRadar — yerel işletme lead keşif ve zenginleştirme sistemi
# Copyright (c) 2026 Furkan Akduman · https://github.com/FlyerFukas
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
#
# Ticari olmayan kullanım serbesttir (bkz. LICENSE).
# İşletmeler ve her türlü ticari kullanım ayrı, ücretli lisans gerektirir.
# Ayrıntı ve iletişim: COMMERCIAL.md
"""SQLite deposu — orijinal Postgres 'marco_leads' tablosunun yerel karsiligi.

Sutunlar, orijinal is akisindaki yapiskan notta verilen SQL semasiyla ayni;
ek olarak 'district' ve 'emails' sutunlari tutulur (raporlama icin faydali).
"""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS marco_leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fingerprint TEXT UNIQUE,
  business_name TEXT NOT NULL,
  category TEXT,
  address TEXT,
  phone TEXT,
  website TEXT,
  public_rating TEXT,
  review_count TEXT,
  website_issues TEXT,
  heuristic_assessment TEXT,
  services_listed TEXT,
  tech_signals TEXT,
  freshness_signal TEXT,
  operating_status TEXT,
  opportunity_score TEXT,
  why_lead TEXT,
  source_links TEXT,
  week_of TEXT,
  discovered_at TEXT,
  district TEXT,
  emails TEXT
);
"""

COLUMNS = [
    "fingerprint", "business_name", "category", "address", "phone", "website",
    "public_rating", "review_count", "website_issues", "heuristic_assessment",
    "services_listed", "tech_signals", "freshness_signal", "operating_status",
    "opportunity_score", "why_lead", "source_links", "week_of", "discovered_at",
    "district", "emails",
]


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def fetch_seen_fingerprints(conn):
    """Orijinal 'Fetch Seen Fingerprints' dugumunun karsiligi."""
    rows = conn.execute(
        "SELECT fingerprint FROM marco_leads WHERE fingerprint IS NOT NULL"
    ).fetchall()
    return {r[0] for r in rows if r[0]}


def insert_lead(conn, lead):
    """Orijinal 'Postgres — Insert Lead' karsiligi.

    INSERT OR IGNORE: ayni parmak izi zaten varsa sessizce atlanir
    (orijinaldeki continueOnFail davranisiyla ayni).
    """
    values = [lead.get(c) for c in COLUMNS]
    placeholders = ", ".join("?" for _ in COLUMNS)
    conn.execute(
        f"INSERT OR IGNORE INTO marco_leads ({', '.join(COLUMNS)}) "
        f"VALUES ({placeholders})",
        values,
    )


def count_leads(conn):
    return conn.execute("SELECT COUNT(*) FROM marco_leads").fetchone()[0]
