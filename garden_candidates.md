# Data Garden Candidates — 2030 AGI Hindsight Filter

## The filter

> It is September 2030. AGI exists. What data do we deeply wish we had been collecting since 2026? What is now entirely useless?

Then combine with all existing filters:
- Irreversibility (temporal, transformational, feedback)
- Transformation difficulty (X > 0)
- Latent quantity, not directly published
- "Everyone wants the answer, nobody publishes it"
- Time moat
- Output leverage

---

## What we'd WISH we had (2026-2030)

### Tier 1 — "We would pay anything for this"

**1. Agent work economics**
- What tasks got delegated to AI agents
- What they cost per task
- Success/failure rates by task type
- Which tasks humans still verified vs trusted blindly
- How agent pricing evolved as models improved

Nobody publishes this. Every company will have done it internally but nobody will have a cross-market view. By 2030 the question "what did autonomous work cost in 2027?" is unanswerable.

**2. Real GPU utilization across the physical economy**
- Not advertised capacity — actual utilization
- Who was idle, who was saturated
- How GPU allocation shifted between AI training, inference, mining, rendering, simulation
- The actual physical bottleneck at each moment

NVIDIA publishes shipments. Cloud providers publish revenue. Nobody publishes "how many GPUs were actually doing useful work at 3am on March 15, 2028."

**3. Inference cost decomposition**
- Not sticker price — effective cost per useful output
- Including: cache hits, batching efficiency, retry overhead, context waste, reasoning-token inflation, subscription amortization
- What a unit of *successful* intelligence actually cost at each point in time

By 2030, "GPT-4 cost $X" is meaningless without knowing what GPT-4 was, what it was being used for, and what the actual quality-adjusted cost was.

**4. Human-AI task boundary migration**
- Which tasks moved from human → AI each month
- At what quality level the transition happened
- What the residual human role became
- Which industries moved fastest

This is the actual story of AGI transition. Nobody is systematically recording it.

**5. Physical constraint migration**
- When GPU shortage → power shortage → cooling shortage → land shortage → permitting shortage
- How the binding constraint moved through the physical economy
- Which constraints relaxed and which tightened as AI scaled

The seesaw at planetary scale. Nobody tracks this as a unified phenomenon.

### Tier 2 — "Extremely valuable, somewhat answerable"

**6. Model capability trajectory (real-world, not benchmarks)**
- Not "GPT-5 scores 92% on MMLU"
- Instead: "GPT-5 can reliably do X, Y, Z tasks that GPT-4 couldn't"
- Task-level capability boundaries over time
- Which capabilities emerged suddenly vs gradually

Benchmarks will be everywhere. Actual task-completion evidence at scale will not.

**7. AI failure mode taxonomy**
- What kinds of failures actually occurred in production
- Frequency, severity, detection latency
- How failure modes evolved as models improved
- What the residual risk looked like at each capability level

By 2030 we'll know what AGI can do. We won't have a clean record of what it couldn't do and why, because nobody logs failures systematically.

**8. Regulatory and governance response timing**
- When each jurisdiction responded to AI
- What triggered the response
- How long between capability emergence and regulation
- What the actual compliance burden looked like

Regulatory history is scattered across government sites, news, and legal databases. A synchronized cross-jurisdictional view will not exist.

**9. Software supply chain dependency mapping**
- Which AI models were actually inside which products
- Version pinning, upgrade cadence, fallback behavior
- When a model upgrade broke downstream systems
- The actual dependency graph of AI in production

Nobody publishes this. By 2030 it's a archaeological question.

**10. Attention migration across knowledge domains**
- What humans searched for, read, shared over 4 years
- How information demand shifted as AI made some knowledge obsolete
- Which topics gained urgency, which became irrelevant
- The actual shape of human intellectual adaptation to AGI

Google has some of this. Nobody has the cross-domain, cross-platform, longitudinal view.

### Tier 3 — "Interesting, harder to argue"

**11. Synthetic vs organic content ratio by domain**
- How much of the internet became AI-generated
- By content type, by platform, by quality level
- When detection became impossible
- How trust protocols evolved

**12. AI energy consumption at grid level**
- Not NVIDIA TDP estimates — actual metered consumption
- By region, by time of day, by workload type
- How datacenter demand affected grid pricing
- The actual energy cost of intelligence

**13. Model drift and capability decay**
- Do models degrade over time without retraining?
- How does performance change with the same weights on new data?
- What the actual maintenance cost of keeping AI systems current was

**14. Cross-border AI arbitrage**
- Where inference was cheapest at each point in time
- Regulatory arbitrage opportunities
- Data sovereignty constraints
- The actual geography of AI economics

**15. Human employment transition microstructure**
- Not "AI replaced X jobs" — the actual week-by-week transition
- Which specific roles changed first
- What the new roles were
- How fast retraining happened

---

## What is USELESS by 2030

**Raw price data** — everywhere, trivially reconstructible

**Social media metrics** — engagement, followers, likes. Meaningless without context. Easily gamed. Low transformation value.

**GitHub stars/forks** — vanity metric. Trivially observable. No transformation needed.

**Generic crypto on-chain data** — chains archive themselves. Block explorers exist. Not a latent quantity.

**Headline news feeds** — archived by dozens of services. No transformation needed.

**Basic hardware specs** — published by manufacturers. Static. Not a latent quantity.

**Generic benchmark scores** — will be everywhere. Don't measure what actually matters (task completion).

**Country-level economic statistics** — published by governments. Already clean. Low transformation value.

**Public company financials** — SEC filings. Already normalized. No moat.

**Weather data** — already commoditized. Multiple free sources.

---

## Garden candidates that pass ALL filters

### Candidate 1: AgentEcon — Agent Work Economics Garden

**Latent quantity:** "What does a unit of autonomous work actually cost?"

**Sources:** API logs (opt-in), provider pricing, task completion records, invoice data, platform telemetry

**Transformation:** Normalize heterogeneous agent pricing (tokens, tasks, subscriptions, credits) into comparable per-task-cost. Decompose into success rate × cost per attempt. Track by task category, model, provider, time.

**Irreversibility:** Pricing changes weekly. Task success rates change with model updates. Historical record disappears.

**2030 test:** "What did it cost to have an AI write a legal brief in March 2027?" — unanswerable without this garden.

**Difficulty:** High — subscription normalization, task decomposition, quality adjustment

### Candidate 2: ConstraintMap — Physical Constraint Migration Garden

**Latent quantity:** "Where is the binding bottleneck in the AI supply chain right now?"

**Sources:** GPU availability APIs, power grid data, datacenter capacity reports, cooling specs, land/permitting databases, shipping/lead times, HBM production data

**Transformation:** Unified constraint tightness index across compute, memory, energy, cooling, land, permitting. Detect constraint migration in real-time.

**Irreversibility:** Constraints shift weekly. The moment a bottleneck relaxes, the evidence of it being binding disappears.

**2030 test:** "When exactly did power become the binding constraint for AI, not GPUs?" — unanswerable without this.

**Difficulty:** Very high — cross-domain normalization, physical measurement

### Candidate 3: InferenceAudit — Effective Intelligence Cost Garden

**Latent quantity:** "What does a unit of useful intelligence actually cost, adjusted for quality?"

**Sources:** Provider APIs, pricing pages, benchmark results, real usage telemetry (opt-in), latency measurements, availability data

**Transformation:** Normalize all pricing models (per-token, per-seat, per-task, subscription, credits) into: $/successful_task, $/inference_second, $/quality_adjusted_unit. Account for cache, batching, retry, context waste.

**Irreversibility:** Pricing changes constantly. Model versions change. The "effective cost of GPT-4-turbo on March 15, 2027" is a historical fact that disappears.

**2030 test:** "What was the cheapest way to get reliable code generation in Q3 2027?" — requires this garden.

**Difficulty:** High — subscription decomposition, quality normalization, throughput measurement

### Candidate 4: TaskBoundary — Human-AI Task Migration Garden

**Latent quantity:** "Which tasks are humans still doing, and how is that changing?"

**Sources:** Job posting analysis, platform telemetry (opt-in), freelance market data, enterprise workflow data, task completion benchmarks

**Transformation:** Categorize tasks by AI-replaceability score. Track migration rate by industry, task type, quality requirement. Build capability boundary map over time.

**Irreversibility:** The transition happens once. You cannot go back and measure "what percentage of legal research was AI-automated in June 2027."

**2030 test:** "When did AI start writing more production code than humans?" — unanswerable retroactively.

**Difficulty:** Very high — task taxonomy, cross-platform normalization, quality assessment

### Candidate 5: ComputeFlow — GPU Allocation Flow Garden

**Latent quantity:** "Where are GPUs actually working, and how does allocation shift?"

**Sources:** Akash/Clore/Nosana provider APIs, mining pool data, cloud provider reports, AI training job scheduling data, rendering farm telemetry

**Transformation:** Unified GPU utilization index across mining, AI training, inference, rendering, simulation. Track allocation flows between use cases in real-time.

**Irreversibility:** GPU allocation shifts daily. The "GPU allocation on March 15, 2027" is gone once it changes.

**2030 test:** "When did AI inference consume more GPU hours than cryptocurrency mining?" — unanswerable without continuous tracking.

**Difficulty:** High — cross-platform normalization, utilization measurement, hardware classification

### Candidate 6: FailureLog — AI Failure Mode Garden

**Latent quantity:** "What actually goes wrong when AI systems are used in production?"

**Sources:** Incident reports (opt-in), API error logs, model evaluation results, safety research, post-mortem analyses, user reports

**Transformation:** Taxonomize failures by type, severity, detection difficulty, model, task, context. Track failure mode evolution over time. Build failure probability models.

**Irreversibility:** Failure events are transient. Post-mortems are scattered. A unified longitudinal failure database will not exist.

**2030 test:** "What was the most common failure mode of code-generation models in 2028?" — nobody will have a systematic answer.

**Difficulty:** Very high — taxonomy design, privacy preservation, severity normalization

### Candidate 7: GridShadow — Energy Constraint Shadow Price Garden

**Latent quantity:** "What is the real marginal cost of powering AI, including grid constraints?"

**Sources:** CAISO/EIA node-level LMP data, datacenter power contracts, grid constraint data, renewable availability, demand forecasts

**Transformation:** Compute shadow prices of physical grid constraints. Isolate AI-driven demand effects. Build location-specific power cost indices for compute.

**Irreversibility:** Grid conditions change every 5 minutes. Shadow prices are ephemeral. Historical grid state is partially reconstructible but AI-specific attribution is not.

**2030 test:** "What was the actual marginal cost of powering an H100 in Northern California in July 2028?" — requires granular, attributed grid data.

**Difficulty:** Very high — grid modeling, demand attribution, constraint identification

### Candidate 8: ModelDrift — AI Capability Decay Garden

**Latent quantity:** "How do AI models actually degrade over time without retraining?"

**Sources:** Model evaluations over time, task completion rates, user complaints, benchmark drift, API performance logs

**Transformation:** Measure capability decay as a function of time, data distribution shift, and task type. Build decay curves for different model families.

**Irreversibility:** The decay of a specific model version on a specific date is ephemeral. Once the model is updated, the old version's behavior on new data is gone.

**2030 test:** "Did GPT-4's code generation quality degrade between January and December 2027?" — requires longitudinal evaluation.

**Difficulty:** High — evaluation design, distribution shift measurement, model access

### Candidate 9: GeoAI — AI Geography Garden

**Latent quantity:** "Where in the physical world is AI actually running, and what does it cost?"

**Sources:** Cloud region availability, datacenter locations, power grid data, internet latency measurements, regulatory filings, GPU delivery addresses

**Transformation:** Build a real-time map of AI infrastructure: where compute exists, what it costs, what constraints it faces, how regulation differs. Track the physical geography of intelligence.

**Irreversibility:** Infrastructure moves, new datacenters come online, regulations change. The "AI geography of March 2027" is a historical fact.

**2030 test:** "Where was inference cheapest in Europe in Q4 2027, and why?" — requires geo-indexed, time-stamped cost data.

**Difficulty:** Very high — multi-source normalization, regulatory tracking, physical infrastructure mapping

### Candidate 10: AttentionGraph — Human Knowledge Demand Garden

**Latent quantity:** "What are humans actually trying to learn, and how is that changing?"

**Sources:** Search trends, educational platform data, forum activity, documentation access patterns, API usage patterns, content consumption data

**Transformation:** Build a dynamic graph of human knowledge demand. Track which topics gain urgency, which become obsolete, which are newly relevant. Map the evolution of human intellectual needs as AI changes what's worth knowing.

**Irreversibility:** Search queries disappear. Forum posts get deleted. Content consumption patterns are ephemeral. The "what humans wanted to know in March 2027" is gone.

**2030 test:** "When did 'how to use ChatGPT' searches peak, and what replaced them?" — requires longitudinal attention data.

**Difficulty:** High — cross-platform normalization, topic modeling, privacy preservation

---

## Ranking by filter score

| Candidate | U | T | X | V | F | Total | 2030 Test |
|-----------|---|---|---|---|---|-------|-----------|
| AgentEcon | 9 | 9 | 8 | 7 | 8 | 41 | Strong |
| ConstraintMap | 9 | 9 | 9 | 8 | 7 | 42 | Strong |
| InferenceAudit | 8 | 9 | 8 | 8 | 8 | 41 | Strong |
| ComputeFlow | 9 | 9 | 7 | 7 | 7 | 39 | Strong |
| TaskBoundary | 8 | 9 | 9 | 6 | 7 | 39 | Strong |
| FailureLog | 7 | 9 | 8 | 7 | 6 | 37 | Medium |
| GridShadow | 8 | 9 | 9 | 8 | 5 | 39 | Medium |
| ModelDrift | 7 | 9 | 7 | 7 | 6 | 36 | Medium |
| GeoAI | 8 | 9 | 8 | 7 | 6 | 38 | Medium |
| AttentionGraph | 8 | 9 | 7 | 6 | 7 | 37 | Medium |
| **PowPowPow** | **9** | **9** | **8** | **8** | **8** | **42** | **Strong** |

---

## The pattern

The strongest candidates all share:

1. **Everyone wants the answer** (cost of AI work, binding constraint, effective price)
2. **Nobody directly publishes it** (requires multi-source transformation)
3. **It changes constantly** (high temporal irreversibility)
4. **The answer is a latent variable** (must be inferred, not scraped)
5. **By 2030 it will be historically unanswerable** (data disappears)

The weakest candidates are all:
- Already published by someone
- Static or slowly changing
- Directly observable
- Low transformation needed
- Reconstructible later
