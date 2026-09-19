# Frontier — How AI research maps to the Data Forest

## The useful connection

What Google DeepMind is showing with Co-Scientist, Aletheia, and SIMA 2 is a general pattern: **generate candidates → evaluate them → preserve useful experience → use that experience to improve the next generation of decisions.**

That pattern maps almost perfectly to the Data Forest system.

---

## 1. Recursive product improvement

We have a genuine environment with measurable rewards:

```text
FOREST STATE
↓
generate content hypothesis
↓
publish Short
↓
REAL HUMAN FEEDBACK
CTR
retention
comments
shares
subs
↓
evaluate hypothesis
↓
change next hypothesis / metric / collector
↓
repeat
```

YouTube is effectively the environment.

Humans provide the external reward.

UKGraph has 200 possible questions. An AI research agent proposes hypotheses. Actual humans tell us whether they had value. Next generation gets that history.

That is a legitimate recursive loop without pretending we're training an AGI.

---

## 2. Jev for the cheap decision layer

TypeSafe's Jev: unstructured state in → typed probabilistic decisions out.

Doesn't generate prose. Returns structured answers plus probabilities. Lower latency/cost than generative LLM workflows.

Exactly what we need for **massive cheap classification and routing**.

Every incoming UKGraph observation:

```text
STATE:
"Government announces requirement X beginning April 2027..."

QUESTIONS:

relevant_market:
[construction, accounting, cyber, healthcare, other]

economic_effect:
[creates_demand, destroys_demand, neutral, uncertain]

audience:
[worker, founder, tradesperson, investor]

worth_deep_analysis:
[yes, no]

urgency:
0-100
```

Ingest far more ugly world data without sending everything through a frontier model.

### Jev inside the YouTube loop

Every prospective video becomes a typed object:

```text
TITLE:
"The UK jobs getting crowded fastest"

QUESTIONS:

specific_audience:
yes/no

economic_consequence:
0-100

answerable_from_data:
0-100

novel_signal:
0-100

likely_repeatable:
yes/no

publish_candidate:
yes/no
```

Run thousands cheaply. Use expensive frontier model only on top few.

```text
                 CHEAP INTELLIGENCE
                       JEV
                        ↓
              classify / route / score
                        ↓
                  promising 1%
                        ↓
                FRONTIER MODEL
           research / reason / script
                        ↓
                    YOUTUBE
                        ↓
                REAL ANALYTICS
                        ↓
               DATASET / MEMORY
                        ↺
```

### Jev gets more useful after analytics

```text
career crowding videos:
median CTR 8.3%
median completion 71%
subscriber conversion 1.9%

AI career risk:
CTR 11.2%
completion 78%
subscriber conversion 2.6%
```

Then bounded questions:

```text
Which audience does this title resemble?
Which prior content cluster is nearest?
Does this look like:
[new_branch, existing_winner, oversaturated_pattern]
Should research budget be:
[none, small, medium, large]
```

The decision layer consumes the garden.

---

## 3. Co-Scientist pattern for discovering new trees

Tournament of ideas: generate, debate, refine, rank, verify against external evidence.

```text
GENERATOR
"What potentially valuable economic questions
could UK workers ask this week?"

↓

CRITIC
"Which are generic bullshit that ChatGPT
could already answer?"

↓

DATA CRITIC
"Which can UKGraph genuinely answer better?"

↓

AUDIENCE CRITIC
"Who specifically gives a shit?"

↓

TITLE GENERATOR
turn question into click-worthy truthful title

↓

VERIFIER
can current data substantiate the answer?

↓

TOURNAMENT
select 10 tests

↓

YOUTUBE
actual humans decide
```

The final tournament judge is reality.

---

## 4. Aletheia gives us the verification loop

```text
generate
↓
verify
├─ correct → ship
├─ minor issue → revise
└─ critically wrong → restart
```

Verifier checks:

```text
Do we actually have evidence?
Are periods comparable?
Is occupation mapping consistent?
Is an apparent change just seasonality?
Are we confusing jobs advertised with worker demand?
```

If evidence fails: DON'T PUBLISH.

The entire channel proposition is: **We answer immediately because we have actual signal.** One garbage confident ranking damages that.

---

## 5. SIMA 2 suggests where this gets autonomous later

SIMA 2 creates new experience through interaction and later uses its own experience data for subsequent training.

Our equivalent experience:

```text
hypothesis
↓
content/action
↓
world response
↓
experience record
```

Eventually millions of decisions:

```text
Given:
audience A
economic state B
metric C
title framing D

Predicted:
strong interest

Observed:
CTR = ...
retention = ...
comments = ...
subscriber conversion = ...
```

Future AI systems have a **real environment-history dataset to improve against**.

We don't need to know what model architecture exists in 2029. We need to produce the kind of experience future models can consume.

---

## 6. Model-agnostic architecture

Don't architect:

```text
JevGraph
GeminiGraph
GPTGraph
```

Architect:

```text
OBSERVATION
↓
DECISION TASK
↓
typed schema
↓
MODEL
↓
decision + confidence
↓
outcome
```

Today:

```text
cheap bounded decision → Jev
complex research       → frontier LLM
verification           → tools + frontier LLM
```

Tomorrow: swap models in. The **forest remains**.

Benefit from rapid AI progress instead of competing against it.

---

## 7. Emerging AI strengthens this strategy

If AI keeps getting better, these approach zero marginal cost:

- Idea generation
- Research per video
- Video creation
- Classification
- Verification
- Coding collectors
- Personalization

What remains valuable:

```text
the feedback history
the audience
the structured environment
the continuously measured economic reality
the correspondence between questions and human reactions
```

---

## 8. The future version

Right now:

```text
one Short → one broad audience
```

Later:

```text
UKGraph state
        ↓
100 audience states
        ↓
AI generates:
  student version
  electrician version
  accountant version
  laid-off programmer version
  founder version
  Manchester version
  Birmingham version
        ↓
distribution
        ↓
analytics
```

The forest learns:

> "28-year-old career switchers in North West England respond strongly to evidence of electrical-specialism shortages but barely respond to generic trade salary rankings."

Jev-style models handle millions of tiny decisions per piece of generative content.

---

## What to implement now

No RSI infrastructure. No model training. No elaborate agent hierarchy.

Just make every tree emit four machine-readable objects:

```text
OBSERVATION    — what happened in the forest
HYPOTHESIS     — what content/audience opportunity we think exists
PUBLICATION    — what we actually published
OUTCOME        — what YouTube reported
```

Then implement:

```text
cheap classifier/ranker    → Jev
frontier researcher        → best current model
verifier                   → explicit evidence checks
analytics ingestion        → YouTube API
experiment store           → permanent structured history
```

---

## The seed worth planting

DeepMind's work shows AI moving toward systems that generate hypotheses, evaluate candidates, learn from interaction, and recursively reuse accumulated experience.

Our advantage: supplying something those systems cannot conjure out of weights.

> **Years of real economic measurements connected to years of actual human reactions to them.**
