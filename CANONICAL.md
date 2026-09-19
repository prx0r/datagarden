# CANONICAL — The Architecture

## The unit of planning is the human sentence, not the project.

### For YouTube:

```text
"What would somebody click?"
        ↓
video title
        ↓
experiment / research
        ↓
interesting result
```

### For Muse/agents:

```text
"What would somebody ask their agent?"
        ↓
capability title
        ↓
required decision
        ↓
required evidence
        ↓
data garden
```

### The two loops feed each other:

```text
YOUTUBE LOOP

interesting question
      ↓
video experiment
      ↓
views / retention / comments
      ↓
proof that people care
      ↓
turn winning question into capability


AGENT LOOP

common user intent
      ↓
capability
      ↓
real usage
      ↓
outcomes / questions / failures
      ↓
new dataset
      ↓
new YouTube investigations
```

### Instead of starting with "what APIs should PowPowPow expose?", start with fake Muse requests.

| Human asks Muse                                                  | Garden    | Capability underneath          |
| ---------------------------------------------------------------- | --------- | ------------------------------ |
| "Can this gaming PC make me money overnight?"                    | PowPowPow | `evaluate_hardware()`          |
| "What should I mine with this GPU today?"                        | PowPowPow | `find_compute_opportunity()`   |
| "Is this Facebook Marketplace camera actually a bargain?"        | Breadup   | `value_object()`               |
| "What should I offer this seller?"                               | Breadup   | `max_offer()`                  |
| "What stuff around me could I flip this weekend?"                | Breadup   | `find_flips()`                 |
| "What businesses are weirdly undersupplied around me?"           | UKGraph   | `find_local_constraints()`     |
| "What could I learn in 3 months that is scarce where I live?"    | UKGraph   | `find_skill_opportunities()`   |
| "Where in Britain are electricians getting unusually expensive?" | UKGraph   | `compare_constraint_regions()` |
| "Make Dad something ridiculous from his dog."                    | Roast.pet | `create_pet_performance()`     |

### Reverse the first column into video titles:

```text
Can Your Gaming PC Actually Make Money While You Sleep?
We Tracked RTX 4090 Mining Profitability Every Hour for 90 Days

Can AI Spot Undervalued Facebook Marketplace Listings?
I Tracked 10,000 eBay Sales to Find What Actually Flips

What Is Britain Running Out Of?
The UK Jobs Nobody Can Fill in 2026

Which UK Skills Are Becoming More Valuable Fastest?
We Built a Map of Britain's Economic Bottlenecks
```

Those videos aren't merely marketing. They're **capability discovery**.

### Jev becomes the standard decision layer

Every winning human question gets transformed into a bounded decision.

```text
VIDEO QUESTION
"Is this Marketplace camera a bargain?"
        ↓
GARDEN
eBay transactions, condition observations, liquidity, fees, seasonality
        ↓
JEV QUESTIONS
P(profitable after costs)?
P(sells within 30 days)?
Choice: BUY / OFFER / WATCH / PASS
        ↓
MUSE CAPABILITY
"Should I buy this?"
```

Same research asset, three outlets:

```text
              DATA GARDEN
                   │
         ┌─────────┼─────────┐
         ↓         ↓         ↓
      YouTube     Muse      API
      insight   capability  developer
```

### The anti-burnout rule

> Don't build a capability until we can write ten compelling natural-language requests for it.
> Don't heavily build it until a corresponding content question shows evidence that humans actually care.

### The operating loop

```text
QUESTION
   ↓
CONTENT
   ↓
ATTENTION SIGNAL
   ↓
RESEARCH
   ↓
DATA
   ↓
JEV
   ↓
CAPABILITY
   ↓
AGENT USAGE
   ↓
OUTCOME DATA
   └────────────→ QUESTION
```

### They're different gardens, but the same machine turns discoveries into media + agent superpowers.
