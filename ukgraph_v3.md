# UKGraph — Sharpened v3 (The Final Form)

## The question we should have been asking

Not "what data should we collect?"

But:

> **What useful outcome currently requires an agent to perform several transformations, joins, searches or historical reconstructions before it can act?**

Then precompute that difficulty and expose it as an endpoint.

That is the Data Garden.

## The endpoint selection formula

$$V = \frac{D \times T \times H \times A \times P}{maintenance}$$

```text
D = desire intensity (money / time / hassle)
T = transformation depth (joins/normalisations required)
H = historical irrecoverability (can't reconstruct later?)
A = actionability (can an agent actually do something?)
P = provability (can we observe whether it worked?)
```

## What passes the test

| Endpoint | D | T | H | A | P | Verdict |
|----------|---|---|---|---|---|---------|
| "Find me a driving test" | ★★★★★ | ★★★ | ★★★★ | ★★★★★ | ★★★★★ | Build |
| "What can I do to make money?" | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★★ | Build |
| "What's this vinyl worth?" | ★★★★ | ★★★★★ | ★★★★★ | ★★★★ | ★★★★ | Build |
| "What should I moisturise with?" | ★★★★ | ★★ | ★ | ★★★★ | ★★ | Don't build |

## What fails the test (frontier model eats it)

```
"Find me a moisturiser"
  → Muse can search current research, read ingredients, reason about intersection

"What's the best restaurant nearby?"
  → Muse can search reviews, read menus, reason about preferences

"Explain how council tax works"
  → Muse can read GOV.UK, explain in plain English
```

## What survives (frontier model can't do it)

```
"What was this vinyl worth over 10 years?"
  → needs historical observations that disappear

"Did my application actually get accepted?"
  → needs receipt verification, not just "I submitted"

"What jobs can I get in Oldham next week?"
  → needs joins: skills × local demand × schedule × certification

"What can I repair and flip with my skills?"
  → needs: capabilities × listing prices × repair economics × time-to-sale
```

## The three primitives (final)

```
uk.do(...)     → UKBoring     "I am lazy"
uk.earn(...)   → UKOpportunity "I want money"
uk.decide(...) → complexity compression across both
```

`I AM AN IDIOT` is not a garden. It's a design constraint:

> Never make Jeff understand the underlying system.

## The central interface

Not hundreds of random endpoints. High-level primitives:

```text
uk.do(goal, context)
uk.earn(profile, constraints)
uk.source(requirement, context)
uk.sell(asset, context)
uk.buy(requirement, context)
uk.resolve(problem, context)
```

Underneath, hundreds of gardens compete to provide candidates.

We sell compressed transformations, not datasets.

## uk.earn() — the killer endpoint

Input:
```json
{
  "place": "Oldham",
  "skills": ["electrician"],
  "certifications": ["NICEIC"],
  "equipment": ["van", "tools"],
  "available_time": ["Thursday 09:00-14:00"],
  "capital": 500,
  "vehicle": "van"
}
```

Output (not "start a YouTube channel"):
```json
{
  "opportunities": [
    {
      "action": "QUOTE_LEAD",
      "description": "Commercial EV installation, 7 miles away",
      "estimated_value": 1200,
      "confidence": 0.89,
      "deadline": "2026-09-25",
      "requirements": ["NICEIC", "van"],
      "route_to_action": "Contact via marketplace"
    },
    {
      "action": "BID_CONTRACT",
      "description": "School electrical maintenance tender",
      "estimated_value": 3500,
      "confidence": 0.72,
      "deadline": "2026-10-01",
      "requirements": ["NICEIC", "insurance"],
      "route_to_action": "Submit via Contracts Finder"
    }
  ]
}
```

## The tradesman market

```
5.7 million UK private-sector businesses
4.3 million with no employees
3.2 million sole proprietorships

The modal UK business is "Dave with a van."
```

Dave doesn't buy "AI CRM software." He says:
> "Muse, run my business."

Muse handles: answer phone, book appointments, send quotes, chase invoices, schedule jobs.

**Where we add value Meta doesn't have:** external economic ground truth.

## The flow

```text
SIGNAL (planning, contract, listing, demand)
    ↓
RETRIEVAL (deterministic filters)
    ↓
SEMANTIC SCORING (Jev — narrow typed questions)
    ↓
RANKING (expected profit × confidence × distance)
    ↓
MUSE (3 actions, not 3,000 records)
    ↓
ACTION
    ↓
RECEIPT
    ↓
OUTCOME
    ↓
GARDEN GROWS
```

## What we learn from outcomes

```
Planning approvals of type X generate electrical leads 3% of the time
Tender type Y looks attractive but Dave-sized firms almost never win
Used equipment predicted £200 margin but realised £72 after parts

→ CALIBRATE opportunity signals against real economic outcomes
→ THAT is the garden
```

## The division of labour

```
Meta knows Jeff.
UKGraph knows what Jeff can do next in the real UK economy.
```

## The first endpoints to build

### I AM LAZY
```
get_me_a_driving_test()
deal_with_this_letter()
move_house_admin()
renew_this()
switch_this_bill()
find_and_book_local_service()
```

### I WANT MONEY
```
find_work_for_me()
find_contracts_for_me()
find_local_leads_for_me()
find_things_i_can_flip()
find_grants_for_me()
find_services_i_could_offer()
```

### Every one returns
```
not: 37 links
but: "Do this. Here's why. Expected upside: £X. Want me to do it?"
```

## The product (one sentence)

> Given everything we know about you and everything we know about Britain, here is exactly what you should do next to make your life better.
