# The Data Garden Thesis — Addendum: The Transformation Requirement

## The forcing function

> **The garden should not merely archive data. It should perform a non-trivial transformation that converts messy reality into a canonical asset.**

If the raw data is already clean, historical, and easily downloadable, elapsed time alone is a weaker moat. Someone can reconstruct most of your history later.

PowPowPow is better because the useful object does **not naturally exist**.

You start with things like:

```text
chain state
exchange prices
pool data
hardware specs
algorithms
power assumptions
emission schedules
difficulty
actual hashrate
market liquidity
```

and transform them into something like:

```text
timestamp
network
algorithm
hardware
effective_hashrate
capex
power_cost
revenue
profitability
break_even_power_price
network_share
market_depth
confidence
provenance
```

That transformation is itself intellectual and operational work.

---

## Three forms of irreversibility

### 1. Temporal irreversibility

You captured something that may disappear.

### 2. Transformational irreversibility

You resolved ambiguities and created a canonical representation that wasn't available directly.

### 3. Feedback irreversibility

Real humans/agents used the transformed object, producing trust, corrections and behavioral data.

---

## The garden equation (revised)

$$
G \approx
U \times T \times X \times V \times F
$$

Where:

- **U** = uniqueness of source observations
- **T** = time/history
- **X** = difficulty of transformation
- **V** = verification/provenance
- **F** = feedback/use

If **X ≈ 0**, be suspicious.

---

## The canonical rule

> **Do not garden information that already exists as information. Garden latent quantities that must be continuously inferred from fragmented reality.**

---

## The test

Every proposed garden must answer:

> **What difficult canonical object are we manufacturing that does not already exist?**

Not:

> What can we scrape?

---

## Applied examples

### PowPowPow

**Raw:** fragmented mining/network/market/hardware data

**Manufactured object:** comparable real-time economics of computational work.

Passes. "Current economically useful mining opportunity" is a latent variable. No chain gives you that field directly.

### LiveLLM

**Raw:** wildly heterogeneous providers, subscriptions, APIs and performance

**Manufactured object:** comparable effective price of machine intelligence.

Requires:

```text
provider
model
billing mechanism
subscription / PAYG / credits
batch discount
cache semantics
reasoning-token treatment
minimum spend
rate limits
effective context
throughput
latency
availability
region
quantization
model identity / alias
date
```

Normalized into:

```text
effective $ / 1M useful tokens
effective $ / successful task
effective $ / inference-second
effective $ / benchmark point
```

Especially hard for subscriptions:

```text
$20/month
"unlimited"
fair-use limits
different models
rolling quotas
priority tiers
```

cannot meaningfully be compared with:

```text
$0.20 / 1M tokens
```

without building a normalization model.

**That normalization is the asset.**

And with actual usage data:

```text
advertised price vs realized price
advertised throughput vs throughput
advertised limits vs observed throttling
```

Now you're measuring the market rather than copying price cards.

---

## The search space

Instead of asking:

> What data can we collect?

Ask:

> **Where does the world contain a valuable quantity that is surprisingly difficult to measure?**

Examples:

**Mining:** "What does a unit of compute actually earn right now?"

**LLMs:** "What does a unit of useful intelligence actually cost?"

**Agents:** "What does a unit of autonomous work actually cost?"

**Datacenters:** "What does immediately usable compute capacity actually cost?"

**Shipping:** "What does moving one standardized unit from A→B actually cost and how long will it really take?"

**Solar/storage:** "What is the real all-in cost of dependable kWh in location X?"

Those are measurements rather than databases.

---

## The best property

> **Everyone wants the answer, but nobody directly publishes the answer.**

That may be the single best forcing function.

---

## What gets rejected

- Basic GitHub trends garden → too reconstructible
- Basic power-price archive → too reconstructible
- Raw vulnerability feed → too reconstructible

---

## The middle box is the farm machinery

```text
MESSY REALITY

100 sources
different units
different definitions
missing values
marketing claims
changing identities
incompatible schemas

        ↓

TRANSFORMATION ENGINE

identity resolution
normalization
verification
derived variables
confidence
causal relationships

        ↓

CANONICAL ASSET

one clean continuously evolving representation
```

---

## The final test

PowPowPow is compelling because **"current economically useful mining opportunity" is a latent variable**. No chain gives you that field directly.

LiveLLM becomes compelling only when it stops being "LLM pricing history" and becomes something closer to a **Bloomberg terminal for the effective price/performance of intelligence**. That is materially harder — and much more defensible.
