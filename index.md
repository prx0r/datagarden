# DataGarden — Index

> Three forests. One question each. AGI is the weather.

---

## The Three Forests

```
                    AGI GRAPH
    capabilities / costs / substitution
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
      BREADUP     POWPOWPOW     ROOM
       THINGS     RESOURCES    MARKETS
```

---

## Breadup (BU) — `/bu/`

> **What is this thing economically worth?**

$$V(object, condition, place, market, time)$$

Fruit: buy / sell / repair / part-out / hold.

| File | Purpose |
|------|---------|
| `thesis.md` | Physical goods value graph |
| `ideology.md` | 15 children, four canonical questions |
| `liquidation_garden.md` | What to buy from failed businesses |
| `repair_garden.md` | Economics of broken things |
| `parts_garden.md` | Canonical replacement-part graph |
| `scrap_garden.md` | Hidden value inside physical waste |
| `used_machine_garden.md` | Breadup for businesses |
| `used_asset_economics.md` | Machinery to vehicles to liquidation |

---

## PowPowPow — `/powpowpow/`

> **Where should scarce computational/physical resources flow?**

$$R(resource, use, location, time)$$

Fruit: allocate compute / power / capital.

| Path | Purpose |
|------|---------|
| `core/` | Resource primitives, panel, BTC baseline, backtests |
| `seesaw_backtests/` | 11 experiments A-K |
| `warehouse.py` | Two-class storage (backfill vs ephemeral) |
| `schema.py` | 26 dataclasses with bitemporal metadata |
| `entities.py` | Permanent IDs for 45 entities |
| `universe.py` | Survivorship bias prevention |
| `manifest.py` | Daily Merkle manifests |
| `source_quality.py` | Longitudinal data confidence |
| `content_system.py` | Content as experiment |
| `experiments.py` | Hypothesis registry |
| `metrics.py` | Versioned equations |
| `counterfactuals.py` | Daily opportunity sets |
| `dead_systems.py` | Failure tracking |
| `thesis.md` | Seesaw thesis |
| `backfill.md` | Backfill vs ephemeral strategy |
| `devmap.md` | Development roadmap |
| `content.md` | Content system architecture |
| `todo.md` | 20 moat foundations |

---

## ROOM — `/room/`

> **Where is there room for me?**

$$M(activity, geography, time)$$

Fruit: work here / start this / enter now / avoid this / sell to these people.

| File | Purpose |
|------|---------|
| `thesis.md` | Market Capacity Graph |
| `business_gap_garden.md` | What business should exist here but doesn't? |
| `trade_demand.md` | Where should I become a tradesman? |
| `local_price_garden.md` | What does work actually cost? |
| `replacement_garden.md` | What is about to need replacing? |
| `regulation_garden.md` | Laws → mandatory spending |

---

## ME (Margin Economics) — `/me/`

> **What does it actually cost to produce an economic outcome?**

$$\text{margin} = \text{market value} - \text{true production cost}$$

Fruit: where are the margins?

| File | Purpose |
|------|---------|
| `index.md` | Where are the margins? |
| `margin_garden.md` | Highest £/hour after inputs |
| `import_arbitrage.md` | Retail–landed-cost spreads |
| `service_arbitrage.md` | AI capability arbitrage |

---

## datagarden/ — `/datagarden/`

> The thesis and architecture layer.

| File | Purpose |
|------|---------|
| `thesis.md` | Full Data Garden thesis (25 sections) |
| `thesis_addendum.md` | Transformation requirement |
| `filters.md` | 13 filters for evaluating gardens |
| `five_primitives.md` | Want / Pain / Price / Supply / Change |
| `garden_candidates.md` | 10 candidates scored by filters |
| `ideology.md` | Economic reality engines |
| `index.md` | This file |

---

## The Pattern

```
INPUT (information)          OUTPUT (money)
─────────────────          ──────────────

BU:       listing + identity + comps → resale margin
PowPowPow: coin + hardware + power → profitability
ROOM:     demand + supply + demographics → market room
ME:       prices + costs + demand → implied £/hour
```

**The input looks like information. The output looks like money.**

---

## The Garden Equation

$$
G =
D \times X \times T \times E \times A \times F
$$

- **D**: difficult/raw data
- **X**: non-trivial transformation
- **T**: irreversible historical accumulation
- **E**: economic decision value
- **A**: audience pull
- **F**: feedback/trust compounding

---

## The Five Primitives

| Primitive | Question |
|-----------|----------|
| **Want** | What do people want? |
| **Pain** | What is currently difficult/expensive/broken? |
| **Price** | What is something really worth? |
| **Supply** | Who can provide it, where and at what capacity? |
| **Change** | What just altered the equilibrium? |

---

## AGI is the weather system

AGI sits above everything. A new capability propagates into all three worlds:

```
VISION + ROBOTICS improves
         │
         ├→ Breadup
         │   object identification /
         │   repair automation improves
         │
         ├→ PowPowPow
         │   compute demand changes
         │
         └→ ROOM
             repair technician economics change
```

You're empirically watching the Seesaw propagate through reality.
