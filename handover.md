# Handover — Next Agent

## The product (one sentence)

> UKGraph continuously compiles messy UK reality into small, actionable, evidence-backed routes for personal agents.

## The three principles

```
I AM LAZY    → UKBoring handles the admin
I WANT MONEY → UKOpportunity shows how
I AM AN IDIOT → dead simple, no learning required
```

## What exists today (verified working)

### MCP Servers (86 tools total)
```
uk_boring_mcp.py     19 tools  — workflows + earn + receipts
breadup_mcp.py       11 tools  — valuation, mispricing, liquidity
ukgraph_mcp.py       12 tools  — economic data (mostly UNAVAILABLE)
powpowpow_mcp.py     12 tools  — mining profitability
council_mcp.py       13 tools  — 8 UK councils
uk_admin_mcp.py      24 tools  — 36 curated tasks
mcp_server.py        23 tools  — unified server
```

### Core kernel
```
core/observation.py    TruthClass, Recoverability
core/route.py          Route object (the canonical outbound object)
core/capability_envelope.py  Privacy boundary (person stays with agent)
core/decision_spec.py  Jev abstraction
core/receipt.py        QP-lite settlement
core/normalize.py      Canonical schemas
core/source_registry.py  Source metadata
core/quality.py        Quality states
core/storage.py        JSONL storage
```

### Data pipeline
```
collectors/ → normalize → canonical/ → MCP tools
```

### UK Boring
```
uk_boring/geo.py        Postcode → Place (postcodes.io)
uk_boring/place.py      Place dataclass
uk_boring/goals.py      7 predefined goals
uk_boring/earn.py       The core endpoint (with Jev)
uk_boring/opportunity.py  Signal processing
uk_boring/national.py   9 UK-wide workflows
uk_boring/workflows/    move_home + 5 painful tasks
boringuk_receipts.py    8 receipt patterns
mcp/uk_boring_mcp.py    19 MCP tools
```

### Canonical data
```
ukopportunity:  604 records (planning + contracts)
ukgraph:       14,294 records (ASHE + HPI + planning)
ukadmin:        37 records (curated tasks) + 24 complaint observations
ukproducts:     107 records (eBay + charity margins)
```

## What's broken (fix these first)

### 1. PowPowPow dependency (18 references to /home/box/powpowpow/)
Makes repo non-portable. Fix: make adapter or copy data.

### 2. earn() returns planning-derived routes only
The 4 routes are all "CONTACT_DEVELOPER" from planning apps. Need contracts + eBay + complaints data to return richer routes.

### 3. Jev called but results not trusted by earn()
Jev classifies relevance but earn() doesn't fully integrate the results. The pre-filter works but the post-Jev ranking is crude.

### 4. No eBay sold data
Blocked from VPS. Need: Apify $5/mo or run locally. Without this, UKProducts has no real sold prices.

### 5. No Companies House data
Waiting for API key. This unlocks business formations/closures for UKOpportunity.

## The key architectural decisions (don't change these)

1. **One connector outward** — agent doesn't know which garden answered
2. **CapabilityEnvelope** — person stays with agent, UKGraph gets minimal context
3. **Route as canonical outbound object** — every result is a Route
4. **Jev as semantic compressor** — not the brain, just the classifier
5. **QP-lite as truth boundary** — receipt verification before claiming success
6. **UNKNOWN is valid** — never silently convert missing data to FALSE

## The naming

```
UKGraph = the whole system
├── UKBoring = "I am lazy" → workflows
├── UKOpportunity = "I want money" → economic signals
└── UKProducts = "What's this worth?" → physical goods
```

## Files to NOT delete

| File | Why |
|------|-----|
| `SPEC.md` | Canonical spec |
| `ukgraph_v3.md` | Endpoint selection formula |
| `ukgraph_final.md` | Final architecture |
| `economic_router.md` | Core product vision |
| `core_insight.md` | Three principles |
| `CANONICAL.md` | Human sentence principle |
| `formula.md` | Moat theory |
| `core/*.py` | Kernel types |
| `mcp/*.py` | All MCP servers |
| `uk_boring/*.py` | Working implementation |
| `tests/*.py` | 26 passing tests |

## The next 10 things to do

1. Fix PowPowPow hardcoded paths (make adapter)
2. Get Companies House API key → collect business data
3. Wire earn() to use contracts + complaints data
4. Get Apify account → collect eBay sold data
5. Build UKGraph MCP with real ASHE data flowing
6. Test earn() end-to-end: "electrician Oldham £300"
7. Build YouTube probe: "Can Your Gaming PC Make Money?"
8. Deploy MCP server for Muse integration
9. Run full pipeline daily (cron working)
10. Measure: does earn() beat ordinary web search?
