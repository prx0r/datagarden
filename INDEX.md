# Datagarden — File Index

Every file in this repo, categorized and labeled.

## Legend

| Label | Meaning |
|-------|---------|
| **LIVE** | Working code, tested, has real data |
| **BUILT** | Working code, tested, needs data or deployment |
| **SEED** | Collectors built, need API keys or local execution |
| **CANON** | Constitutional document (don't delete, don't change lightly) |
| **THINK** | Thinking/architecture document (reference, not implementation) |
| **HISTORY** | Superseded but preserved for context |
| **DEAD** | No longer relevant, kept for archive |

---

## Root files

| File | Label | What it is |
|------|-------|-----------|
| `README.md` | LIVE | Project overview and quick start |
| `SETUP.md` | LIVE | Installation and API key setup |
| `requirements.txt` | LIVE | Python dependencies |
| `.env.example` | LIVE | Environment variables template |
| `.gitignore` | LIVE | Git ignore rules |
| `handover.md` | CANON | **Read this first.** What exists, what's broken, what's next |
| `northy.md` | CANON | The northstar: economic matching formula |
| `economic_router.md` | THINK | The core product vision — what we're building |
| `core_insight.md` | THINK | I AM LAZY + I WANT MONEY + I AM AN IDIOT |
| `todo.md` | THINK | Engineering doctrine — Jev as semantic compiler |
| `CANONICAL.md` | CANON | Architecture reference (constitution) |
| `formula.md` | CANON | Moat theory (constitution) |
| `architecture.md` | THINK | Muse + Jev + QP-lite + Data Garden stack |
| `pain_points.md` | THINK | Consumer + business pain points |
| `ukgraph_final.md` | THINK | Final naming and architecture |
| `ukgraph_v3.md` | THINK | Endpoint selection formula |
| `ukgarden.md` | THINK | UKGraph as geographic substrate |
| `dev_plan.md` | THINK | 5-phase implementation plan |
| `boringuk.md` | THINK | Workflow garden concept |
| `boringuk_receipts.md` | THINK | Receipt verification patterns (doc) |
| `implementation.md` | THINK | Implementation status (stale, needs update) |
| `index.md` | HISTORY | Original project structure (outdated) |
| `unified2.md` | HISTORY | Earlier unified system doc |
| `alpha_stack.md` | HISTORY | Early stack design |
| `content_strat.md` | HISTORY | Content strategy |
| `content_map.md` | HISTORY | Content mapping |
| `filters.md` | HISTORY | Filter definitions |
| `five_primitives.md` | HISTORY | Original five primitives |
| `frontier.md` | HISTORY | AI research connection |
| `garden_candidates.md` | HISTORY | Candidate garden ideas |
| `ideology.md` | HISTORY | Ideology document |
| `os.md` | HISTORY | Operating system concept |
| `thesis.md` | HISTORY | Original thesis |
| `thesis_addendum.md` | HISTORY | Thesis additions |
| `human_tasks.md` | HISTORY | Human tasks (overlaps SETUP.md) |
| `boringuk_receipts.py` | BUILT | Receipt verification engine |

---

## core/ — Kernel types

| File | Label | What it is |
|------|-------|-----------|
| `__init__.py` | LIVE | Exports all types |
| `observation.py` | LIVE | Raw immutable record + TruthClass + Recoverability |
| `entity.py` | LIVE | Permanent thing being observed |
| `source.py` | LIVE | Data source with cadence/recoverability/health |
| `derived.py` | LIVE | Computed from observations with method+version |
| `capability.py` | LIVE | Answer to human question + ActionClass |
| `outcome.py` | LIVE | What actually happened (feedback loop) |
| `storage.py` | LIVE | Thread-safe append-only JSONL |
| `hardware.py` | BUILT | HardwareEconomics type (device × algo → profit) |
| `valuation.py` | BUILT | BreadupValuation type (evidence chain) |
| `workflow.py` | BUILT | Workflow + WorkflowStep types |

---

## uk_boring/ — UKBoring implementation

| File | Label | What it is |
|------|-------|-----------|
| `__init__.py` | LIVE | Exports all |
| `place.py` | LIVE | Place: resolved location with jurisdictions |
| `geo.py` | LIVE | Postcode → Place via postcodes.io (free) |
| `ontology.py` | LIVE | 14 core types (Service, Rule, Workflow, etc.) |
| `national.py` | LIVE | 9 national primitives (DVLA, electoral, etc.) |
| `workflows/move_home.py` | LIVE | 7-step move-home workflow |
| `oldham.py` | BUILT | Oldham place definition + 5 services |
| `goals.py` | BUILT | 7 predefined goals across 3 outlets |
| `opportunity.py` | BUILT | Signal processing (planning, business, contract) |
| `earn.py` | BUILT | uk.earn() — the core product endpoint |
| `api.py` | BUILT | FastAPI server structure |
| `scaling.md` | THINK | National vs local override architecture |
| `tests/test_move_home.py` | LIVE | 4 tests passing |

---

## mcp/ — MCP servers

| File | Label | Tools | What it is |
|------|-------|-------|-----------|
| `uk_boring_mcp.py` | LIVE | 17 | UKBoring: workflows + earn + receipts |
| `breadup_mcp.py` | LIVE | 11 | Breadup: valuation, mispricing, liquidity |
| `ukgraph_mcp.py` | LIVE | 12 | UKGraph: economic data (mostly UNAVAILABLE) |
| `powpowpow_mcp.py` | LIVE | 12 | PowPowPow: mining profitability |
| `council_mcp.py` | LIVE | 13 | Council services (8 councils) |
| `uk_admin_mcp.py` | LIVE | 24 | UK Admin: 36 curated tasks |
| `../mcp_server.py` | LIVE | — | Unified server (root level) |

---

## collectors/ — Data collectors

| File | Label | What it is |
|------|-------|-----------|
| `planning_collector.py` | BUILT | Planning Data API (free) — parses entities |
| `contracts_collector.py` | BUILT | Contracts Finder API (free) — 100 contracts collected |
| `ons_jobs.py` | SEED | ONS + GOV.UK labour data |
| `uk_admin_collectors.py` | LIVE | 36 curated tasks seeded |
| `mot_history.py` | SEED | DVSA MOT History (needs API key) |
| `ukgraph_historical.py` | SEED | ASHE + Nomis + Land Registry |
| `breadup_historical.py` | SEED | eBay/ING/Kaggle/NBER |
| `powpowpow_historical.py` | SEED | CoinGecko/Minerstat |
| `companies_house.py` | SEED | Companies House streaming |
| `ebay_free.py` | SEED | eBay public search (VPS-blocked) |
| `ebay_sold.py` | SEED | eBay via Apify (needs key) |
| `run_daily.py` | BUILT | Daily orchestrator |

---

## shared/ — Infrastructure

| File | Label | What it is |
|------|-------|-----------|
| `normalize.py` | BUILT | Canonical schemas + normalization for all gardens |
| `jev.py` | BUILT | TypeSafe Jev integration |
| `warehouse.py` | BUILT | Storage layer (fixed: relative paths) |
| `entities.py` | BUILT | Entity registry (fixed: relative paths) |
| `manifest.py` | BUILT | Daily Merkle manifest (fixed: relative paths) |
| `experiment.py` | LIVE | PublicationExperiment dataclass |
| `schema.py` | BUILT | Original schema (mostly PowPowPow-specific) |
| `uk_admin_schema.py` | BUKT | UK Admin task schema |

---

## tests/

| File | Tests |
|------|-------|
| `test_core.py` | 15: Observation, Entity, CapabilityResult, Outcome, Storage |
| `test_breadup.py` | 4: Truth contract on MCP tools |
| `test_ukgraph.py` | 4: Truth contract, no fake scores |
| `test_ukadmin.py` | 3: Workflow verification honesty |
| `test_normalize.py` | 4: Normalizer roundtrip |

---

## Other directories

| Directory | Status | What's there |
|-----------|--------|--------------|
| `capabilities/` | BUILT | `evaluate_hardware.py` — PowPowPow probe capability |
| `content/` | BUILT | Video pipeline + 3 generated Shorts |
| `content/shorts/` | GENERATED | 4 mp4 + 4 mp3 + 4 png from test run |
| `docs/` | BUILT | `muse_connector_submission.md` |
| `experiments/` | BUILT | Jev question templates + 3 experiment logs |
| `forests/breadup/` | SEED | `skus.py` (100 SKUs) + data dirs |
| `forests/ukgraph/` | BUILT | Planning + contracts data (100 records) |
| `forests/uk_admin/` | BUILT | 36 curated tasks + verified workflows |
| `resources/` | THINK | Data source catalogs for all 4 gardens |
| `canonical/` | SEED | Normalized data (auto-generated) |

---

## Summary counts

| Category | Count |
|----------|-------|
| LIVE files | ~25 |
| BUILT files | ~20 |
| SEED files (need data) | ~10 |
| THINK docs (architecture) | ~15 |
| HISTORY docs (superseded) | ~12 |
| Dead/unused | 0 (everything has a purpose) |
| **Total Python** | **59 files** |
| **Total Markdown** | **42 files** |
