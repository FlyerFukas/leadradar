# -*- coding: utf-8 -*-
# LeadRadar — yerel işletme lead keşif ve zenginleştirme sistemi
# Copyright (c) 2026 Furkan Akduman · https://github.com/FlyerFukas
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
#
# Ticari olmayan kullanım serbesttir (bkz. LICENSE).
# İşletmeler ve her türlü ticari kullanım ayrı, ücretli lisans gerektirir.
# Ayrıntı ve iletişim: COMMERCIAL.md
"""Istege bagli yapay zeka cilasi.

Varsayilan olarak KAPALIDIR. Acmak icin config.json:
    "ai": {"enabled": true, "provider": "anthropic"}
ve ortam degiskeni: ANTHROPIC_API_KEY  (provider=openai icin OPENAI_API_KEY)

Gereken paket: pip install anthropic   (veya: pip install openai)

Ne yapar: Her aday icin 'neden aday?' gerekcesini, sezgisel degerlendirmeyi ve
gorusme acilis onerisini, denetim kanitlarina dayanarak dil modeliyle yeniden yazar.
Ne YAPMAZ: Firsat skorunu degistirmez — skor daima kural tabanlidir (guardrail).
"""

import json
import os

_SCHEMA = {
    "type": "object",
    "properties": {
        "why_lead": {"type": "string"},
        "heuristic_assessment": {"type": "array", "items": {"type": "string"}},
        "outreach_tip": {"type": "string"},
    },
    "required": ["why_lead", "heuristic_assessment", "outreach_tip"],
    "additionalProperties": False,
}

_PROMPT = """Sen bir web tasarimcisi icin lead raporu yazan asistansin.
Asagida bir yerel isletme adayinin verileri ve web sitesi denetim kanitlari var.

SADECE su uc alani Turkce olarak yeniden yaz:
- why_lead: 1-2 cumle, YALNIZCA verilen kanitlara dayan; kanitta olmayan hicbir sey uydurma.
- heuristic_assessment: her satiri "[HEURISTIC] " ile baslayan izlenim listesi (kanit degilse buraya).
- outreach_tip: isletme sahibiyle gorusme acilisi icin nazik, somut bir oneri cumlesi.

Skoru degistirme, yeni olgu ekleme. Veriler:
{payload}
"""


def _build_payload(item):
    return json.dumps(
        {
            "lead": {k: item["lead"].get(k) for k in
                     ("business_name", "category", "district", "address", "phone",
                      "website", "website_tier")},
            "scored": item["scored"],
            "audit_evidence": {
                k: (item["audit"] or {}).get(k) for k in
                ("objective_issues", "heuristic_issues", "tech_signals", "https",
                 "viewport", "http_status", "copyright_year", "emails",
                 "phones_on_site", "contact_links", "title")
            } if item["audit"] else None,
        },
        ensure_ascii=False,
    )


def _polish_one_anthropic(client, model, item):
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": _PROMPT.format(payload=_build_payload(item))}],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )
    if response.stop_reason == "refusal":
        return None
    text = next((b.text for b in response.content if b.type == "text"), "")
    return json.loads(text)


def _polish_one_openai(client, model, item):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _PROMPT.format(payload=_build_payload(item))
                   + "\nYaniti SADECE ham JSON nesnesi olarak ver: "
                     '{"why_lead": ..., "heuristic_assessment": [...], "outreach_tip": ...}'}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def polish(enriched, cfg):
    provider = cfg["ai"].get("provider", "anthropic")

    if provider == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY tanimli degil")
        import anthropic  # pip install anthropic
        client = anthropic.Anthropic()
        model = cfg["ai"].get("model") or "claude-opus-4-8"
        polish_one = lambda item: _polish_one_anthropic(client, model, item)
    elif provider == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY tanimli degil")
        from openai import OpenAI  # pip install openai
        client = OpenAI()
        model = cfg["ai"].get("model") or "gpt-5.1"
        polish_one = lambda item: _polish_one_openai(client, model, item)
    else:
        raise RuntimeError(f"Bilinmeyen saglayici: {provider}")

    for item in enriched:
        try:
            result = polish_one(item)
        except Exception as exc:  # tek aday tum calistirmayi durdurmasin
            print(f"        AI cilasi atlandı ({item['lead']['business_name']}): {exc}")
            continue
        if not result:
            continue
        # Skor asla degismez — yalnizca metin alanlari guncellenir
        item["scored"]["why_lead"] = result["why_lead"]
        item["scored"]["heuristic_assessment"] = result["heuristic_assessment"]
        item["outreach_tip"] = result["outreach_tip"]
