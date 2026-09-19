# Handover — Next Agent

## What this repo is

UKGraph: a continuously verified execution-and-opportunity graph for Britain. The economic router that matches what people CAN do to what the UK economy NEEDS right now.

```
UKGRAPH = the whole datagarden
├── UKBoring      "I am lazy" → do it for me
├── UKOpportunity "I want money" → show me how
└── UKProducts    "What's this worth?" → price it
```

## The three principles

```
I AM LAZY    → UKBoring handles the admin
I WANT MONEY → UKOpportunity shows how
I AM AN IDIOT → dead simple, no learning required
```

## The product

> Given everything we know about you and everything we know about Britain, here is exactly what you should do next to make your life better.

## The core endpoint

```python
uk.earn(profile={
    location: "Oldham",
    skills: ["electrician"],
    certifications: ["NICEIC"],
    available_days: ["Thursday", "Saturday"],
    capital: 500
})
# Returns: grounded actions with estimated value, confidence, route to action
```

## What exists (working)

### MCP Servers (all import successfully)

| Server | Tools | Status |
|--------|-------|--------|
| `mcp/breadup_mcp.py` | 11 | ✅ |
| `mcp/ukgraph_mcp.py` | 12 | ✅ |
| `mcp/powpowpow_mcp.py` | 12 | ✅ |
| `mcp/council_mcp.py` | 13 | ✅ |
| `mcp/uk_admin_mcp.py` | 24 | ✅ |
| `mcp/uk_boring_mcp.py` | 14 | ✅ |
| **Total** | **86** | |

### Core kernel

`core/` — Observation, Entity, Source, DerivedFact, CapabilityResult, Outcome, HardwareEconomics, BreadupValuation, Workflow

### UK Boring

- Place system (UPRN → jurisdictions → services)
- Geo resolver (postcodes.io, free)
- 14 ontology types
- Oldham prototype
- Move-home workflow (7 steps, receipt verification)
- 9 national primitives (DVLA, electoral, HMRC, vehicle tax)
- Receipt verification engine (8 patterns)
- Goal definitions (7 goals)
- Opportunity signal processing
- `uk.earn()` endpoint

### Collectors

- `collectors/planning_collector.py` — Planning Data API (free)
- `collectors/contracts_collector.py` — Contracts Finder (free)
- `collectors/ons_jobs.py` — ONS + GOV.UK
- `collectors/uk_admin_collectors.py` — 36 curated tasks
- `collectors/mot_history.py` — DVSA MOT History (needs API key)
- `collectors/breadup_historical.py` — eBay/ING/Kaggle/NBER
- `collectors/ukgraph_historical.py` — ASHE/Nomis/Land Registry
- `collectors/powpowpow_historical.py` — CoinGecko/Minerstat

### Tests

26 tests passing (core, breadup, ukgraph, ukadmin, normalize)

## What's broken (fix these first)

### 1. Hardcoded paths to /home/box/powpowpow

5 files reference this path. Won't work for anyone else.

**Files:**
- `mcp_server.py:658,694,721,757,789`
- `mcp/powpowpow_mcp.py:32-33`
- `capabilities/evaluate_hardware.py:19,49`
- `collectors/powpowpow_historical.py:31,37`

**Fix:** Either make PowPowPow an adapter that reads from its own repo, or copy the needed data into datagarden's canonical directory.

### 2. shared/ files still PowPowPow-specific

- `shared/warehouse.py` — hardcodes canonical path, subdirectories only know mining chains
- `shared/entities.py` — all entities are PowPowPow-specific
- `shared/schema.py` — mostly mining dataclasses

**Fix:** These should be garden-agnostic or moved to PowPowPow-specific code.

### 3. Naming chaos

| Name | What it means |
|------|---------------|
| UKGraph | The whole datagarden (ukgraph_final.md) OR one garden (economy.md) |
| Breadup | Physical goods garden = UKProducts |
| UK Admin / Boring UK / UKBoring | The workflow garden |
| ROOM / UKGraph / UKOpportunity | The economic opportunity garden |
| ME / Margin Economics | Production economics (not implemented) |

**Fix:** Adopt `ukgraph_final.md` naming:
- UKGraph = whole system
- UKBoring = workflows
- UKOpportunity = economic signals
- UKProducts = physical goods

### 4. Stale markdown files

These are superseded and should be removed or archived:
- `moat.md` (contradicted by `formula.md`)
- `plant.md` (superseded by `plant2.md`)
- `ukgraph_v2.md` (superseded by `ukgraph_v3.md`)
- `ukgraph_sharpened.md` (superseded by `ukgraph_v3.md`)
- `boringuk_v2.md` (superseded by `boringuk.md`)
- `unified.md` (superseded by `unified2.md`)
- `economy.md` (implemented, no longer needed)
- `plant2.md` (overlaps with `handover.md`)
- `seed_data.md` (overlaps with `implementation.md`)

### 5. Overstated claims in implementation.md

- "Breadup: 10 tools ✅" — actually 4 tools in mcp_server.py
- "UKGraph: 10 tools ✅" — actually all UNAVAILABLE (no data)
- "PowPowPow: 12 tools ✅" — depends on broken external repo imports

### 6. CAPABILITY.md references functions that don't exist

`value_object()`, `max_offer()`, `find_flips()`, `find_local_constraints()`, `find_skill_opportunities()`, `compare_constraint_regions()`, `create_pet_performance()` — none of these exist in code.

## What's the next priority

1. **Fix hardcoded paths** — make the repo portable
2. **Clean up naming** — adopt ukgraph_final.md naming everywhere
3. **Remove stale files** — delete superseded markdown
4. **Fix shared/ to be garden-agnostic**
5. **Build the earn endpoint properly** — with real data feeds
6. **Deploy MCP server** — make it accessible to agents
7. **Run collectors** — fill the data gaps
8. **Build YouTube probe** — "What can I do to make money in Oldham?"
9. **Submit to Muse** — connector when ready
10. **Measure outcomes** — QP verification loop

## Key documents to read

| Document | What it tells you |
|----------|-------------------|
| `northy.md` | The northstar: economic matching formula |
| `ukgraph_v3.md` | Endpoint selection formula, uk.earn() |
| `economic_router.md` | The core product vision |
| `core_insight.md` | I AM LAZY + I WANT MONEY + I AM AN IDIOT |
| `architecture.md` | Muse + Jev + QP-lite + Data Garden stack |
| `boringuk_receipts.md` | How receipt verification works |
| `uk_boring/earn.py` | The uk.earn() implementation |

## Key files to NOT delete

| File | Why |
|------|-----|
| `CANONICAL.md` | The architecture reference (constitution) |
| `formula.md` | The moat theory (constitution) |
| `northy.md` | The northstar |
| `ukgraph_v3.md` | The endpoint selection formula |
| `economic_router.md` | The product vision |
| `core_insight.md` | The three principles |
| `uk_boring/*.py` | The working implementation |
| `mcp/*.py` | All 6 MCP servers (86 tools) |
| `core/*.py` | The kernel types |
| `tests/*.py` | 26 passing tests |

## External dependencies

| Dependency | Status | Fix needed |
|------------|--------|------------|
| `/home/box/powpowpow/` | 5 files reference it | Make adapter or copy data |
| `/home/box/qprivately/` | Referenced in architecture.md | Archive reference only |
| `/home/box/influence/` | Referenced in architecture.md | Archive reference only |

## The data situation

| Garden | Data | Status |
|--------|------|--------|
| PowPowPow | 17 chains with live data | ✅ Working (external repo) |
| Breadup | 0 sold records | ⚠️ Collectors built, need local run |
| UKGraph | 68 ONS records + ASHE downloads | ⚠️ Partial |
| UK Boring | 36 curated tasks, 5 verified | ✅ Working |

## The honest assessment

The architecture is sound. The vision is clear. The code works where it touches real data.

The main weakness: **too many markdown files describing what should exist, not enough code making it exist.**

The next agent should:
1. Pick ONE thing (probably `uk.earn()` for electricians in Oldham)
2. Make it work end-to-end with real data
3. Ignore everything else until that one thing works
4. Let the garden grow from actual usage
