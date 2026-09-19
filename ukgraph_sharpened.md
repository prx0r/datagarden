# UKGraph — Sharpened Architecture

## Competition landscape

### Direct competitors (data aggregation)

| Competitor | What they do | Threat level |
|------------|-------------|--------------|
| **UKDataAPI** | 25 endpoints, 400+ gov sources, MCP server, €39/mo | HIGH — already ahead on aggregation |
| **HomeData** | 29M properties, EPC, risk scores, price history | MEDIUM — property focus only |
| **PropertyData** | 150+ data points, £0.50/property, ML predictions | MEDIUM — property focus only |
| **Street Data** | 150+ data points, 29M properties, £0.50/property | MEDIUM — property focus only |
| **PlanningAPI UK** | 2.4M applications, 400+ councils, <200ms | HIGH — planning focus |
| **PlanningInsights** | Planning application data and insights | MEDIUM |
| **PlanIt** | 420 councils, 20.6M applications, free API | LOW — we use this as source |
| **CouncilData.co.uk** | 350 councils, council tax bands | LOW — we use this as source |

### What they DON'T do

| Capability | UKDataAPI | HomeData | PropertyData | PlanningAPI | **UKGraph** |
|------------|-----------|----------|--------------|-------------|-------------|
| Data aggregation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Workflow execution | ✗ | ✗ | ✗ | ✗ | **✅** |
| Receipt verification | ✗ | ✗ | ✗ | ✗ | **✅** |
| Geographic joins | partial | ✗ | ✗ | ✗ | **✅** |
| Economic signals | ✗ | ✗ | ✗ | ✗ | **✅** |
| Local trades routing | ✗ | ✗ | ✗ | ✗ | **✅** |
| Outcome tracking | ✗ | ✗ | ✗ | ✗ | **✅** |

### The differentiator

**They aggregate data. We execute workflows and verify outcomes.**

UKDataAPI can tell you "this company is at risk." We can:
1. Tell you the risk
2. Explain what to do about it
3. Guide you through doing it
4. Verify it actually happened
5. Track the outcome over time

That's the gap.

### The £100M opportunity

UK government launched £100M Sovereign AI R&D Procurement Scheme (Aug 2026):
- NHS productivity challenge
- AI agent security testing
- Compute efficiency
- Defence AI

This is literally funded demand for what we're building.

## Structural flaws to address

### 1. Data aggregation race is already lost
Don't try to beat UKDataAPI at aggregation. They have 400+ sources. We have ~20.

**Instead:** Use their data as a source. Build the layer they don't have: execution + verification + outcomes.

### 2. Planning data is crowded
PlanningAPI UK, PlanningInsights, PlanIt all exist.

**Instead:** Don't be another planning API. Be the system that acts on planning signals. "Planning approved" → "here's what needs to happen next" → "here's who can do it" → "done."

### 3. Property data is commoditized
HomeData, PropertyData, Street Data all compete on data points and price.

**Instead:** Don't sell property data. Sell "I moved to Oldham, sort everything." The property data is context, not the product.

### 4. The workflow execution moat is real but fragile
Nobody else is doing receipt verification + QP settlement. But it requires:
- Verified receipt patterns (we have 8)
- Actual browser execution (Muse)
- Outcome tracking (QP-lite)

**Build this fast before someone else does.**

### 5. The geographic joins are the real asset
Nobody is joining:
- planning + jobs + businesses + contracts + services + workflows

That's the moat. Build the join graph, not the data layers.

## What's actually valuable

### For consumers (Muse users)

| Pain point | What they ask | What we provide |
|------------|--------------|-----------------|
| "I'm moving" | Sort my admin | Move-home workflow with receipt verification |
| "Is this a good area?" | Local intelligence | Economic data + planning + services |
| "Who can fix this?" | Find a tradesperson | Local routing via Checkatrade/Taskrabbit |
| "What do I need to do?" | Government obligations | Workflow expansion from life events |
| "What's changing here?" | Local signals | Planning + business + economic changes |

### For businesses

| Pain point | What they ask | What we provide |
|------------|--------------|-----------------|
| "Where should I open?" | Market intelligence | Business gaps + economic data |
| "Who needs my services?" | Demand signals | Planning-derived demand + skills gaps |
| "What contracts are available?" | Procurement | Contracts Finder integration |
| "What's the competition doing?" | Business intelligence | Company formations/closures by area |
| "Where are wages rising?" | Labour market | ASHE data + skills shortages |

### For developers/agents

| Pain point | What they ask | What we provide |
|------------|--------------|-----------------|
| "Give me Nottingham data" | API access | Structured regional API |
| "What can this property do?" | Planning constraints | Planning Data API integration |
| "What workflows are available?" | MCP tools | Workflow execution via MCP |
| "Did it actually work?" | Verification | QP receipt verification |

## The end results for Muse users

### Consumer journey

```
User: "I'm moving to Oldham next Friday"

Muse → UKGraph API
  → resolve_place(postcode="OL1 1AA")
  → Place: Oldham, Council X, Ward Y
  
Muse → UKGraph API
  → move_home workflow
  → 7 steps identified (5 national, 2 local)
  
Muse → user
  "I can handle 5 of these steps for you.
   I need your council tax reference and move date.
   2 steps require you to do them directly."

User provides info

Muse executes steps 1-5
QP verifies each confirmation
Garden stores verified outcomes

Muse → user
  "Done. Your driving licence is updated (ref DL-2026-12345).
   Electoral registration submitted.
   Council tax notified.
   Your MOT check shows it expires March 2027.
   Want me to find a plumber for the new place?"
```

### Business journey

```
User: "I'm thinking of opening a cafe in Nottingham"

Muse → UKGraph API
  → economic data for Nottingham
  → business formations, closures, gaps
  
Muse → UKGraph API
  → planning applications (new developments nearby)
  → footfall signals
  
Muse → user
  "Nottingham had 180 new food businesses last year,
   120 closed. Net growth is positive but competitive.
   There are 3 planning approvals for residential
   within 500m of NG1 — that's future footfall.
   Want me to check specific sites?"
```

### Developer journey

```
Agent → UKGraph MCP
  → resolve_place(postcode="M1 1AE")
  
Agent → UKGraph MCP
  → list_national_workflows()
  → 9 workflows available everywhere
  
Agent → UKGraph MCP
  → get_area_workflows(area_id="manchester")
  → 3 additional local workflows
  
Agent uses workflows to help user
QP verifies outcomes
Garden grows
```

## The renamed architecture

```
UKGRAPH
├── UKProducts    (formerly Breadup — physical goods)
├── UKGraph       (formerly UKGraph — economic data per place)
├── UKBoring      (formerly UK Admin — workflow execution)
└── UKOpportunities (formerly UKGraph economic layer)
```

Wait — that's confusing. Let me simplify:

```
UKGRAPH = the unified platform
├── places (geo resolver → jurisdictions → services)
├── economic (jobs, wages, businesses, property)
├── workflows (government tasks with receipt verification)
├── routing (trades, services, providers)
├── signals (planning, changes, opportunities)
└── outcomes (verified results + garden history)
```

One platform. Multiple lenses. One graph.
