# northy.md — UKGraph Northstar

## The product

> Given everything we know about you and everything we know about Britain, here is exactly what you should do next to make your life better.

## The question

> What useful outcome currently requires an agent to perform several transformations, joins, searches or historical reconstructions before it can act?

## The endpoint selection formula

$$V = \frac{D \times T \times H \times A \times P}{maintenance}$$

D = desire intensity
T = transformation depth
H = historical irrecoverability
A = actionability
P = provability

## The three verbs

```
uk.do(...)      → UKBoring      "I am lazy"
uk.earn(...)    → UKOpportunity "I want money"
uk.decide(...)  → complexity compression across both
```

## The division of labour

```
Meta knows Jeff.
UKGraph knows what Jeff can do next in the real UK economy.
```

## The first-order product

"What opportunities exist near me?"

## The deeper product

"Given what I can actually do, what am I unusually well-positioned to make money from right now?"

## The economic matching formula

```
Expected Utility =
  P(success) × payoff
  - time
  - capital
  - risk
  - friction

subject to:
  skills, certifications, location, calendar,
  equipment, capital, preferences
```

Muse provides the right-hand side (Jeff's context).
UKGraph continuously learns the left-hand side (the economy).

## The feedback loop

```
UKGraph sees opportunity
    ↓
Muse matches Jeff
    ↓
Jeff acts
    ↓
QP verifies economic outcome
    ↓
UKGraph learns which match actually worked
    ↓
next recommendation improves
```

## The garden discovers relative advantage

Initially: "opportunity exists"
Later: "who was shown it, who pursued it, who won it, how much it paid, what skills predicted success"

Then:
```
Skill scarcity
Opportunity/person fit
Expected £/hour
Expected £/£ capital
Competition
Travel friction
Win probability
Time until opportunity expires
```

## The I WANT MONEY verbs

```
EARN
├── WORK      take this job
├── SELL      sell this asset
├── FLIP      buy broken, repair, resell
├── BUILD     start offering this service
├── INVEST    put capital where returns are
├── SAVE      switch provider / reduce cost
└── UPGRADE   spend now to earn more later
```

## The downstream signals

```
SKILL SCARCITY: "Which capabilities are becoming valuable?"
TRAINING ROI: "Which qualification should Jeff acquire next?"
GEOGRAPHIC ARBITRAGE: "Would Jeff earn more 20 miles away?"
CAPITAL ALLOCATION: "What £500 purchase increases earning capacity most?"
EQUIPMENT ROI: "Would buying this tool unlock enough work?"
CAREER TRANSITION: "Shortest path from current to more valuable?"
BUSINESS CREATION: "What service could Jeff offer that nobody nearby provides?"
PRICING: "Jeff is probably undercharging relative to current scarcity."
SCHEDULING: "Which opportunity is the highest-value use of Thursday?"
FLIPPING: "What assets can Jeff uniquely repair/resell?"
```

## The economic scarcity map

```
LOCATION × CAPABILITY × DEMAND × TIME
```

AGI makes this more valuable, not less. As intelligence commoditises, the question becomes:
> What scarce real-world capabilities does Jeff control?

Licensed electrician, physical location, van, tools, trusted history, legal permission, capital, availability, manual dexterity.

AI can't manufacture those.

## The strict rule

UKGraph does NOT build Jeff's giant private profile.

We accept a task-specific capability envelope:
```json
{
  "location": "Oldham",
  "skills": ["electrician"],
  "certifications": ["NICEIC"],
  "equipment": ["van", "tools"],
  "available_time": 8,
  "capital": 500
}
```

Return opportunities. That keeps us useful without becoming surveillance.

## The tagline

> **We do not tell people generic ways to make money. We continuously measure where real economic opportunity exists and match it to capabilities they already control.**

## QP closes the loop

UKGraph predicted: "opportunity exists"
Muse acts
QP verifies: "did they actually make money?"

That accumulated dataset is the garden.
