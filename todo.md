# todo.md — The Engineering Doctrine

## Jev as semantic compiler

Jev turns the economic router from "a bunch of APIs" into a continuously running semantic machine.

```
RAW UK ECONOMY
      ↓
     JEV (cheap, continuous, typed)
      ↓
structured economic features
      ↓
UKGraph
```

For every item in the firehose (50K jobs, 20K listings, 5K planning apps, 2K tenders...), Jev makes tiny semantic judgments:

```text
Noul: Could a sole trader perform this?
Noul: Does this require a van?
Choice: primary capability = ELECTRICAL/PLUMBING/BUILDING/IT/CLEANING
Score: small-business accessibility = 0..1
Score: application friction = 0..1
```

## Three AIs, three jobs

| AI | Role | Cost |
|----|------|------|
| **Muse** | Expensive personalised intelligence | What does Tom want? Should we act? |
| **Jev** | Cheap ambient intelligence | Classify everything, score everything, find semantic relationships |
| **Frontier model** | Deep occasional work | Research novel areas, design workflows, investigate anomalies |

## The compiled data pattern

Raw web → UKGraph compiles → agent sees end result.

```
BAD:  search_jobs(oldham)
GOOD: economic_routes(place=Oldham, capabilities=[...], availability=this_weekend)
```

Underneath: 17 sources → 4,000 observations → 600 entity resolutions → 150 Jev judgments → 3 outputs.

**That compression is the product.**

## The test

> Does this endpoint give the agent something meaningfully expensive to reconstruct itself?

```
search_jobs()         → ChatGPT can do that
beauty_products()     → Muse can do that
economic_routes()     → UKGraph does that (multi-source, historical, semantic)
market_value(vinyl)   → UKGraph does that (10 years of disappearing data)
cancel_route()        → UKGraph does that (verified current path)
```

## The engineering doctrine

```
DON'T:  get_planning_records() get_jobs() get_council_data()
DO:     earn() value() cancel() resolve() do()

Even better:
        route(goal, context)
```

## Jev creates the latent economic graph

Nobody publishes:

```
requires_van?
customer_facing?
weekend_compatible?
learnable_quickly?
transferable_from_mechanic?
requires_legal_qualification?
likely_automatable_by_ai?
```

Jev continuously transforms prose into these probabilistic features.

Nobody publishes:

```
motorbike_repair ──.82──> mower_repair
domestic_electrician ──.91──> EV_installation
music_interest ──.72──> festival_work
van_ownership ──.88──> bulky_item_flipping
```

## Verified receipts make Jev calibrate

```
predicted fit .9 → actual success 87%
predicted fit .6 → actual success 58%
predicted fit .3 → actual success 29%
```

That's the feedback loop. Jev predicts → outcome verifies → calibration improves.

## CancelMe as canonical UKBoring example

```
service × billing_channel × country × account_state × current_policy
    ↓
exact exit route
    ↓
observable proof that you're actually out
```

Gary sees: "Cancel this."
He doesn't care which subsystem solved it.

## The final system

```
THE UK ECONOMY
      ↓
  continuous observations
      ↓
     JEV (semantic compressor)
      ↓
   UKGRAPH (compiled reality)
      ↓
  economic routes
      ↓
     ×
      ↓
   MUSE (understands Tom)
      ↓
  "This is unusually good for you."
      ↓
     ACT → RECEIPT → verified outcome → UKGRAPH
```

**That feedback arrow is the company.**

## The description of UKGraph

> UKGraph continuously compiles messy UK reality into small, actionable, evidence-backed results for personal agents.

The moat is the compiler getting better through historical observations + transformations + verified outcomes.

## ChatGPT validates the data layer

We don't need Muse in Britain to prove the thesis.

Give ChatGPT:
```
ukgraph.earn(...)
ukgraph.cancel(...)
ukgraph.value(...)
```

Compare:
- Without UKGraph: search, search, infer, maybe stale, generic
- With UKGraph: 3 grounded routes, current as-of dates, evidence, action URL

If the second feels dramatically better, we've validated the transformation.

Remote MCP is the correct neutral interface.
