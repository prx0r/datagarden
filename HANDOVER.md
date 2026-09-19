# Handover — Full Audit & Organization Guide

## What this repo IS

UKGraph: a continuously verified, machine-actionable model of what exists, what applies, what is happening, what is needed, what is available, and what can be done at every place in Britain.

```
UKGRAPH = shared spatial/economic spine
├── UKBoring      "I am lazy" → do it for me
├── UKOpportunity "I want money" → show me how
└── UKProducts    "What's this worth?" → price it
```

## What this repo is NOT

- A data catalogue
- A search engine
- Another Indeed
- Another Checkatrade
- Another GOV.UK explainer
- A giant ontology project
- An attempt to store every fact about Britain
- A replacement for Muse/ChatGPT

## The three principles

```
I AM LAZY    → UKBoring handles the admin
I WANT MONEY → UKOpportunity shows how
I AM AN IDIOT → dead simple, no learning required
```

---

## OPEN THREADS (things that need resolution)

### 1. PowPowPow dependency (CRITICAL)
**18 references** to `/home/box/powpowpow/` across 5 files. Makes repo non-portable.
- `mcp_server.py:658-845` — worst offenders
- `mcp/powpowpow_mcp.py:32-33`
- `capabilities/evaluate_hardware.py:19,49`
- `collectors/powpowpow_historical.py:31,37`

**Fix:** Either make PowPowPow an adapter that reads from its own repo, or copy needed data into canonical/.

### 2. earn() doesn't work end-to-end
`uk.earn()` exists but depends on real data feeds (planning, contracts, eBay) that haven't been collected at scale.
**Fix:** Run collectors, wire into earn endpoint, test with real scenario.

### 3. MCP tool count overstated
- `handover.md:51` says 86 tools
- Actual count: ~23 in unified server
- Individual servers have more but many return "no_data"
**Fix:** Count actual functional tools, not definitions.

### 4. Naming inconsistency
- `ukgraph_final.md`: UKGraph = whole system
- `implementation.md`: UKGraph = one garden
- `boring.md`: old naming (BU/PG/ME)
**Fix:** Adopt `ukgraph_final.md` naming everywhere.

### 5. Manifest verification bug
`verify_manifest_integrity()` calls `generate_manifest()` which mutates the file being verified.
**Fix:** Make verification read-only.

### 6. Jev never actually called
`shared/jev.py` imports typesafe_sdk but no code ever calls it.
**Fix:** Wire into earn pipeline or remove.

### 7. Content strategy from old naming
`content_map.md`, `content_strat.md`, `ideology.md` reference ROOM, ME, BU — superseded naming.
**Fix:** Archive these or update references.

---

## STALE CONTENT (preserved with comments)

### Files that are superseded but preserved
| File | Status | What replaced it |
|------|--------|------------------|
| `index.md` | HISTORY | `INDEX.md` |
| `implementation.md` | STALE | Actual code is the truth |
| `ukgraphfinal_cloud.md` | DUPLICATE | Exact copy of `SPEC.md` |
| `boringuk_receipts.md` | REDUNDANT | `boringuk_receipts.py` is source of truth |
| `human_tasks.md` | OVERLAPS | `SETUP.md` for quick start |
| `five_primitives.md` | THEORY | Not implemented, old naming |
| `filters.md` | THEORY | Not implemented, old naming |
| `content_map.md` | STALE | Old naming (ROOM, ME, BU) |
| `content_strat.md` | STALE | Old naming |
| `ideology.md` | STALE | Old naming (BU/PG/ME) |
| `garden_candidates.md` | ASPIRATIONAL | 2030-focused, no code |
| `unified2.md` | ASPIRATIONAL | References non-existent projects |
| `frontier.md` | ASPIRATIONAL | DeepMind projects, not implemented |

### What to do with stale files
Don't delete. Add comment at top:
```markdown
<!-- STALE: This document describes an earlier naming scheme or unimplemented concept.
     Preserved for context. Current architecture is in ukgraph_final.md and SPEC.md. -->
```

---

## BROKEN REFERENCES

| Reference | Where | Issue |
|-----------|-------|-------|
| `/home/box/powpowpow/` | 18 files | Hardcoded, non-portable |
| `forests/room/` | README.md | Directory doesn't exist |
| `forests/me/` | README.md | Directory doesn't exist |
| `os/` | README.md | Directory doesn't exist |
| `thesis/` | README.md | Directory doesn't exist |
| Roast.pet | CANONICAL.md, capabilities.md | No code exists |
| `typesafe-sdk` | requirements.txt | May not be installed |
| `edge_tts` | content/pipeline.py | May not be installed |

---

## WHAT ACTUALLY WORKS (verified)

| Component | Status | Evidence |
|-----------|--------|----------|
| Core kernel (core/) | ✅ 14 types, all import | Tests pass |
| UKBoring MCP | ✅ 19 tools, all import | Tools return data |
| Place system | ✅ postcodes.io resolves | Real API calls work |
| National primitives | ✅ 9 UK-wide workflows | Defined and testable |
| Planning collector | ✅ 100+ applications | Data in forests/ |
| Contracts collector | ✅ 100 contracts | Data in forests/ |
| UK Admin tasks | ✅ 36 curated | Data seeded |
| Content pipeline | ✅ 3 Shorts generated | content/shorts/ |
| Normalize pipeline | ✅ 14,000+ records | canonical/ |
| Earn endpoint | ✅ Returns routes | Reads canonical store |
| Receipt verification | ✅ 7 patterns | Testable against GOV.UK |

---

## WHAT DOESN'T WORK YET

| Component | Issue | Fix needed |
|-----------|-------|------------|
| earn() end-to-end | Needs real data feeds | Run collectors |
| PowPowPow tools | Depend on external repo | Make adapter |
| eBay scraping | VPS blocked | Run locally |
| Jev integration | Never called | Wire into pipeline |
| Muse connector | Never submitted | Deploy MCP server |

---

## THE PRODUCT (one sentence)

> UKGraph continuously compiles messy UK reality into small, actionable, evidence-backed routes for personal agents.

## THE FIRST VERTICAL

Oldham electrician makes £500 this weekend.
- earn() returns 3+ routes from planning + contracts
- Each route has evidence, confidence, action
- Receipt verification proves it worked
- Garden grows with every outcome

## WHAT TO DO NEXT

1. **Fix PowPowPow dependency** (make adapter, don't hardcode)
2. **Run collectors at scale** (planning + contracts + ONS)
3. **Wire earn() to real data** and test end-to-end
4. **Deploy MCP server** for Muse integration
5. **Run the probe video** and measure attention
6. **One thing at a time** — don't build more platform until earn() works
