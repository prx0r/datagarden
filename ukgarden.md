# UKGraph — The Northstar

> **Don't own the Nottingham webpage. Own the Nottingham joins.**

## The thesis

UKGraph is the continuously verified, machine-actionable model of what exists, what applies, what is happening, what is needed, what is available, and what can be done at every place in Britain.

When an agent needs to know or do something whose answer materially depends on a place, querying our graph is easier and more reliable than reconstructing that place from the open web.

## The architecture

```text
                         UKGRAPH

                           UK
                            │
                    ┌───────┴───────┐
                 national         places
                   rules             │
                             ┌───────┴────────┐
                         Nottingham         Oldham
                             │
     ┌──────────┬────────────┼───────────┬──────────┐
   people    businesses   property     govt       live
   needs       supply      planning   services    signals
     │            │           │           │          │
     └────────────┴───────────┴───────────┴──────────┘
                              │
                         opportunities
                              │
                ┌─────────────┼────────────┐
               jobs        purchases    actions
             contracts       services    forms
               grants         leads      bookings
                              │
                           ROUTERS
                              │
             Checkatrade / Taskrabbit / GOV.UK /
              council portals / shops / agents
```

## The 12 core objects

| Object | What it is | Example |
|--------|-----------|---------|
| **Place** | Resolved location with all jurisdictions | Nottingham, OL1 1AA, UPRN 123456789012 |
| **Service** | Government or local service available at a Place | Council tax, waste, parking, planning |
| **Rule** | Deterministic rule that applies at a Place | "Band D council tax = £1,850" |
| **Workflow** | Executable sequence to achieve an outcome | Move home, register to vote, check MOT |
| **Form** | A form that needs to be filled | DVLA address change, council tax move |
| **Requirement** | What's needed for a workflow step | Identity, address, registration number |
| **Evidence** | An observation with source and timestamp | "Council tax band D, £1,850/year" |
| **Action** | An execution step in a workflow | Fill form, submit, capture confirmation |
| **Outcome** | What actually happened after an action | "Application received, ref DL-2026-12345" |
| **Provider** | A local provider | Checkatrade plumber, Taskrabbit electrician |
| **Offer** | A commercial offer attached to a workflow | "Plumber: £85/hr, available tomorrow" |
| **Signal** | A detected change or pattern | "Planning approved: 12 flats on Mansfield Road" |

## The join is the moat

Anyone can scrape Nottingham City Council.

The valuable object is the continuously maintained graph joining:

```text
place → rules → people's needs → businesses → jobs →
contracts → properties → services → live conditions →
executable actions → verified outcomes
```

## What UKGraph knows that nobody else joins

```text
PLANNING APPLICATION APPROVED
       ↓
future demand
       ├── electricians
       ├── plumbers
       ├── scaffolding
       ├── waste
       ├── flooring
       ├── kitchens
       ├── broadband
       ├── EV charging
       └── property management

JOIN Companies House:
       which suppliers exist locally?

JOIN Procurement:
       has the public sector bought related services?

JOIN Labour:
       are relevant skills locally scarce?

JOIN Prices:
       is this category becoming constrained?
```

Planning feed → economic precursor feed.

## The data sources underneath

| Source | What it gives | Status |
|--------|--------------|--------|
| Companies House API | Live company data | ✅ Free API |
| Nomis API | Local labour-market data | ✅ Free API |
| Land Registry PPD | Transaction-level property data | ✅ Free download |
| Police.uk | Street-level crime/outcome data | ✅ Free API |
| Planning Data API | 100+ planning/housing datasets | ✅ Free API |
| Contracts Finder | 34,968 awarded contracts (2025/26) | ✅ Free API |
| GOV.UK Content API | All government services | ✅ Free, no key |
| postcodes.io | Postcode → jurisdiction resolution | ✅ Free, no key |
| ONS ASHE | Earnings by occupation × region | ✅ Free download |
| ONS Claimant Count | Monthly local labour signal | ✅ Free API |
| Bus data | Timetables, fares, real-time locations | ✅ Free |
| EV charger data | Location, connector, tariff, availability | ✅ Free (regulation) |

## The scaling formula

```text
1 national workflow (move_home)
  × 400 councils
  × local overrides
  = 400 localized workflows
  from ONE implementation
```

80% national, 20% local.

## The business model — eight lenses over one graph

| Outlet | What it does | Revenue |
|--------|-------------|---------|
| Muse/MCP | "What can I do here?" + execute workflows | Connector fees |
| Consumer router | Send demand into marketplaces | Lead/referral |
| Opportunity engine | Jobs, grants, contracts, planning signals | Subscription |
| Local business intelligence | "What is changing within 5 miles?" | API access |
| Property intelligence | Planning, development, transactions, services | API access |
| Economic API | Structured datasets for agents/companies | API access |
| GeoEvent feed | Subscribe to changes in a geographic area | Subscription |
| Research/public sector | Anonymised operational outcomes | Grants/contracts |

## The first vertical

Build:

```text
UK BORING
       ↓
Geo resolver
       ↓
OLDHAM ROOM
       ↓
MOVE HOME
       ↓
LOCAL TRADES ROUTING
       ↓
CONTRACTS/OPPORTUNITIES
```

Do ONE complete chain, then measure:

```text
how much of the graph is inherited vs locally overridden
```

That ratio tells us whether this scales across Britain.

## The north star

```text
UKGraph
=
a continuously verified,
machine-actionable model
of what exists,
what applies,
what is happening,
what is needed,
what is available,
and what can be done
at every place in Britain.
```
