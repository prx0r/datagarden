# Plant 2 — The First Nine Probes

## The unit we plant

```text
TREE

1. audience
2. clickable question/title
3. hypothesis: why this audience should care
4. exact answer we need to produce
5. minimum transformation required
6. minimum live data required
7. Short generated from the answer
8. YouTube analytics returned
9. decision: prune / keep / deepen
```

---

## The explicit prediction

Before publishing anything:

```text
TITLE:
"The UK jobs getting crowded fastest"

TARGET:
UK 20–35yo considering retraining

WHY WE THINK IT HITS:
- career uncertainty is economically consequential
- crowding is counterintuitive versus generic "high demand jobs"
- answer can change a real decision
- strong fear/curiosity gap without withholding information

EXPECTED SIGNAL:
high CTR
high first-10s retention
comments naming careers people are considering
```

Then reality tells us whether that belief was correct.

We aren't merely optimizing videos. We're learning:

> **which pieces of economic information different humans value.**

---

## The first nine trees

| Forest | First tree | First Short |
|--------|-----------|-------------|
| **UKGraph** | Career crowding | **The UK jobs getting crowded fastest** |
| **UKGraph** | Market room | **The UK jobs where demand is outrunning workers** |
| **UKGraph** | New economic openings | **The new UK markets opening right now** |
| **Breadup** | Mispricing | **Things people are selling too cheaply right now** |
| **Breadup** | Liquidity | **The used products that sell fastest** |
| **Breadup** | Repair economics | **Broken things actually worth buying** |
| **PowPowPow** | Resource return | **The most profitable compute hardware right now** |
| **PowPowPow** | Resource migration | **The networks miners are quietly leaving** |
| **PowPowPow** | Constraint change | **The compute bottlenecks getting worse fastest** |

Nine trees is enough. Not 200.

Each one produces **one canonical metric** repeatedly.

---

## Tree examples

### UK Job Crowding Tree

```text
raw:
vacancies
wages
entrant supply
job-posting trajectory
training/qualification supply

transform:
crowding score

output:
occupation ranking

content:
"The UK jobs getting crowded fastest"

API eventually:
GET /ukgraph/career-crowding
```

### Breadup Mispricing Tree

```text
raw:
live listings
product identity
condition
market comparisons
sale/liquidity observations

transform:
estimated fair value - current asking price

output:
ranked underpriced objects

content:
"Things people are selling too cheaply right now"

API:
GET /breadup/mispricing
```

### PowPowPow Resource Return Tree

```text
raw:
hardware cost
resource contribution
rewards
energy
network state

transform:
normalized resource return

output:
ranked allocation opportunities

content:
"The most profitable compute hardware right now"

API:
GET /powpowpow/resource-return
```

---

## One shared schema from day one

Every tree logs the same experiment structure:

```text
tree_id
forest
child
audience

title
title_hypothesis
why_we_expect_interest

metric
answer
confidence

published_at

impressions
ctr
views
retention_3s
retention_10s
completion
likes
comments
shares
subs_generated

decision
prune | continue | deepen

next_hypothesis
```

The loop:

```text
we think people care about X
↓
we measure X
↓
we publish X
↓
people reveal whether they care
↓
we alter the next measurement
```

---

## Two severe rules

> **No new collector gets built unless it powers a specific title we intend to publish.**

Prevents sliding back into giant-data-platform mode.

> **No video gets made unless it is backed by a measurement we want to keep collecting.**

Prevents becoming generic AI content sludge.

---

## The immediate mission

Not "build Breadup / UKGraph / PowPowPow."

> **Plant 3 trees in each forest, get each one producing an answer, and publish the first nine probes.**

Then YouTube starts telling us what the forest wants to become.
