# Dev Plan — UKGraph Groundwork

## Current state (what exists)

```
core/                  8 files   — kernel types (Observation, Entity, Source, etc.)
uk_boring/            11 files   — Place, Geo, Goals, Workflows, Oldham, API, National
mcp/                   6 files   — Breadup, UKGraph, PowPowPow, UKAdmin, Council, UKBoring
shared/                7 files   — Warehouse, Entities, Manifest, Schema, Normalize, Jev
collectors/           11 files   — eBay, ONS, Companies House, ASHE, UKGraph, PowPowPow
content/               3 files   — Pipeline, Shorts generator
tests/                 5 files   — Core, Breadup, UKGraph, UKAdmin, Normalize
boringuk_receipts.py   1 file    — Receipt verification patterns
```

## What needs to exist for the first working demo

### The demo: "What can I do to make money in Oldham right now?"

```text
Jeff says to Muse: "I want to make some extra money this weekend"

Muse calls: uk.earn(profile={skills:["electrician"], location:"Oldham", available:["Saturday"]})

UKGraph returns:
- 2 EV install enquiries (worth ~£400 each)
- 1 council electrical maintenance contract
- 3 broken items on eBay that match Jeff's repair skills (estimated margin £80-160)
- 1 grant for EV certification training

Muse says: "The EV install jobs are your best bet. Want me to contact them?"
```

## Dev plan

### Phase 1: Foundation (this session)

- [x] Core kernel (Observation, Entity, Source, DerivedFact, CapabilityResult, Outcome)
- [x] Place system (geo resolver, Oldham prototype)
- [x] Goal definitions (7 goals across 3 outlets)
- [x] Move-home workflow with receipt verification
- [x] National primitives (DVLA, electoral, HMRC, vehicle tax)
- [x] UKBoring MCP server (14 tools)
- [x] Opportunity signal processing
- [x] Receipt verification engine (8 patterns)

### Phase 2: Data feeds (next)

- [ ] Planning data collector (Planning Data API → UKGraph)
- [ ] Contracts Finder collector → UKOpportunity
- [ ] Companies House feed → UKOpportunity
- [ ] eBay sold prices → UKProducts (Apify or local)
- [ ] ONS labour market → UKOpportunity
- [ ] EV charger data → UKOpportunity

### Phase 3: The earn endpoint (core product)

- [ ] `uk.earn(profile)` implementation
- [ ] Capability matching (skills × demand)
- [ ] Opportunity scoring (Jev + deterministic)
- [ ] Route to action (how to actually do it)
- [ ] MCP endpoint for Muse

### Phase 4: Outcome tracking

- [ ] QP-lite receipt verification for earn outcomes
- [ ] Outcome database (signal → action → result)
- [ ] Calibration (which signals actually predict money?)

### Phase 5: Distribution

- [ ] Free MCP server deployment
- [ ] Muse connector submission
- [ ] Trade business profiles (free websites)
- [ ] YouTube probe videos
