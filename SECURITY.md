# Security Policy

## API keys are never stored in this repository

LeadRadar reads every credential from your own machine at runtime:

| Key | Where it is read from |
|---|---|
| `FIRECRAWL_API_KEY` | Environment variable, or the Firecrawl CLI credential file |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | Environment variable (only when `ai.enabled` is true) |

Nothing is hardcoded, and `.gitignore` excludes `.env`, `credentials.json` and `*.key`.
If you fork this project you use **your own** accounts and your own quota.

## Scraped data stays local

`output/` (PDF and JSON reports) and `data/leads.db` contain real business contact
details. Both are excluded from version control by `.gitignore`. **Do not commit them** —
publishing third-party contact data may breach privacy law (GDPR in the EU).

## Responsible use

- The crawler is deliberately slow (delay between requests, one page request per site).
- Only publicly available business information is collected.
- LeadRadar never sends messages on your behalf; outreach is always a human decision.
- Business data comes from OpenStreetMap under the
  [ODbL](https://www.openstreetmap.org/copyright) — keep the attribution if you
  redistribute derived data.

## Reporting a vulnerability

Open an issue at
[github.com/FlyerFukas/leadradar/issues](https://github.com/FlyerFukas/leadradar/issues).
Please do not include real API keys or personal data in the report.
