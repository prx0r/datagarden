# UK Government MCP Servers — Integrated Resources

## Cloned and available

| Server | Tools | What it does | Location |
|--------|-------|-------------|----------|
| `legislation-mcp-ts` | 7+ | legislation.gov.uk — search UK statutes | `/home/box/legislation-mcp-ts/` |
| `GovUK-MCP` | 33 | Companies House, TfL, NHS, Parliament, Police | `/home/box/GovUK-MCP/` |
| `govuk-mcp` | 7 | GOV.UK search, content, organisations, postcodes | `/home/box/govuk-mcp/` |

## legislation-mcp-ts — UK Law

Tools:
- `search_legislation` — keyword search across all UK statutes
- `get_legislation` — full text of any statute
- `get_legislation_metadata` — structured metadata
- `get_legislation_fragment` — specific section/part
- `search_effects` — legislative amendments/repeals
- `search_powers_and_duties` — who has power to do what (needs backend)

Requires: Node.js 18+
Setup: `cd legislation-mcp-ts && npm install && npm start`

## GovUK-MCP — 33 Government APIs

Tools include:
- Companies House (company search, officers, filings)
- Parliament (MPs, voting records, debates)
- NHS (hospital finder, GP search)
- Transport (TfL status, journey planner)
- Police (crime data by area)
- Charity Commission
- And more

Requires: Python 3.10+
Setup: `cd GovUK-MCP && pip install -e .`

## govuk-mcp — GOV.UK Content

Tools:
- `govuk_search` — full-text search across 700K+ pages
- `govuk_get_content` — page metadata and section index
- `govuk_get_section` — body HTML for a section
- `govuk_grep_content` — regex search within a page
- `govuk_get_organisation` — government org details
- `govuk_list_organisations` — all UK government orgs
- `govuk_lookup_postcode` — postcode → local authority

No API key required. Can run as remote server: `https://govuk-mcp.fly.dev/mcp`

## How these integrate with UKGraph

```
UKGraph
├── legislation-mcp-ts → "What laws apply here?"
├── GovUK-MCP → "What services exist? Who's my MP?"
├── govuk-mcp → "What does GOV.UK say about X?"
├── council_mcp.py → "What can my council do?"
├── uk_admin_mcp.py → "How do I do X?"
└── uk_boring_mcp.py → "Sort this out for me"
```

The existing MCP servers provide the raw government data layer.
UKGraph provides the transforms: workflow routing, receipt verification, outcome tracking.
