# UKGraph — Sharpened v2

## The thesis (sharpened)

> **UKGraph is a continuously verified execution-and-opportunity graph for Britain: what applies at a place, what can be done, what evidence is required, where the action happens, and what actually happened afterward.**

## The moat

Not aggregation (UKDataAPI already has 400+ sources). Not data (government gives it away free). The moat is:

```text
cross-domain joins
+
personal/local context
+
actionability
+
verified outcome history
```

Nobody owns all four.

## What we DON'T compete with

| Competitor | What they do | We don't compete on |
|------------|-------------|---------------------|
| GOV.UK Chat | "How do I renew X?" | Government Q&A |
| UKDataAPI | Data aggregation | Raw data layer |
| PlanningAPI UK | Planning applications | Planning data alone |
| HomeData | Property data | Property intelligence alone |
| Resolver | Complaint resolution | Single-domain workflows |
| Policy in Practice | Benefits calculation | Benefits calculation |

## What we DO build

| Our layer | What it is | Why it's defensible |
|-----------|-----------|---------------------|
| **Goal graph** | What people actually want to accomplish | Derived from real usage, not invented |
| **Workflow execution** | Actually doing things, not just explaining | Receipt verification = proof |
| **Cross-domain joins** | planning × jobs × businesses × contracts × services | Nobody joins all of these |
| **Outcome history** | What actually happened after action | Time-bound, path-dependent |
| **Opportunity signals** | Planning → demand → business → jobs | Derived, not scraped |

## The architecture

```
                UKGRAPH
            shared place spine
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    UKBORING  UKOPPORTUNITY UKPRODUCTS
      │           │           │
  workflows     signals     markets
   actions      jobs        products
  receipts     tenders       prices
  friction     grants      liquidity
               leads
```

## The three outlets

### UKBoring — "get annoying real-world things done"

```
Goal: MOVE_HOME
  → verified multi-institution workflow

Goal: DEAL_WITH_LETTER
  → obligation resolved / response acknowledged

Goal: FIX_HOME_PROBLEM
  → qualified provider booked

Value metric:
  verified outcomes completed / user effort required
```

### UKOpportunity — "what can I earn, win, exploit, build or sell here?"

```
Goal: FIND_LOCAL_WORK
  → tenders/contracts → business fit → qualified opportunities

Goal: WHAT_CHANGED
  → legislation + council + planning + business + demand

Goal: OPEN_LOCATION
  → population + footfall + vacancy + competition + property
```

### UKProducts — "what physical things are worth, wanted and moving?"

```
Goal: SELL_ITEM
  → pricing + liquidity + platform routing

Goal: BUY_ITEM
  → valuation + negotiation + verification

Goal: FLIP_ITEM
  → acquisition cost + margin + timeline
```

## The AI stack (final)

```
┌────────────────────────────────────┐
│                MUSE                │
│ user context, planning, browser,   │
│ long-running work, approvals       │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│             UKGRAPH API            │
│ place, goals, workflows, facts,   │
│ opportunities, routing             │
└───────┬────────────────┬───────────┘
        │                │
        ▼                ▼
     CODE/RULES          JEV
  deterministic      semantic decisions
     decisions       (inside workflows)
        │                │
        └───────┬────────┘
                ▼
             ACTION
                │
                ▼
            READBACK
                │
                ▼
           QP-LITE
                │
                ▼
            DATA GARDEN
```

Jev belongs INSIDE workflows, not above them.

## Execution classes (final)

```
AUTO           Muse executes fully
APPROVAL       Muse prepares, user approves
AUTH_HANDOFF   User takes over for login/identity
DECLARATION    User must personally attest
HUMAN_ONLY     Cannot currently be agent-completed
```

## The hard rule

> **Every new dataset must answer: which user Goal becomes materially better because this exists?**

No answer → don't collect it yet.

## The product

Not a database. Not an API. Not a chatbot.

The product is the increasing amount of Britain that has gone from:

```
messy web + institutions + local knowledge
```

to:

```
machine-understandable
→ machine-actionable
→ independently verifiable
→ historically learned
```

## What to build first

Three complete Goals that exercise three future businesses:

```
UKBORING:    MOVE_HOME → verified multi-institution workflow
UKOPPORTUNITY: FIND_LOCAL_PUBLIC_WORK → tenders → qualified opportunities
UKPRODUCTS:  SELL_OR_BUY_USED_ITEM → local physical-object economics
```

All share: Place, Organisation, Person-context, Time, Evidence, Outcome.

If these three coexist cleanly on the same graph without coupled spaghetti, the architecture is validated.
