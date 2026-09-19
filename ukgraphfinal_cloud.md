This freezes the strongest conclusions while preserving the original Data Garden invariant: **unique transformation × continuous collection × time**, and “only collect data when we can continuously transform it into a proprietary measurement worth preserving.” 

# UKGraph

**Status:** Canonical working specification
**Version:** 0.1
**Purpose:** Thesis, architecture, engineering specification, operating manual, and definition of done.

This document is deliberately **not static doctrine**. The invariants are intended to remain stable. Implementations, gardens, sources, DecisionSpecs, proof rules, ranking methods and outlets are expected to evolve from evidence.

---

# 0. One-sentence definition

> **UKGraph continuously compiles messy UK reality into small, actionable, evidence-backed routes for personal agents.**

It does not replace the personal agent.

It provides the parts that a frontier agent cannot cheaply or reliably reconstruct at query time:

* disappearing historical state,
* cross-source transformations,
* local economic scarcity,
* entity and product identity resolution,
* semantic normalization,
* real-world workflow knowledge,
* verified outcome history.

The end product is not “data”.

The end product is:

```text
PERSON + GOAL
      ×
CURRENT UK REALITY
      ↓
ACTIONABLE ROUTE
      ↓
AGENT ACTS
      ↓
VERIFIED OUTCOME
      ↓
UKGRAPH LEARNS
```

---

# 1. Constitutional principles

Everything in UKGraph must survive these principles.

## 1.1 The three human principles

```text
I AM LAZY
I WANT MONEY
I AM AN IDIOT
```

These are product constraints, not insults.

### I AM LAZY

Do not make the user:

* search,
* compare twenty links,
* learn a government process,
* monitor listings,
* manually track deadlines,
* repeatedly enter information,
* understand how UKGraph works.

Return the next useful action.

### I WANT MONEY

Where economically relevant, optimize toward real outcomes:

```text
money earned
money saved
asset value realised
time saved
earning capacity increased
risk avoided
```

Do not substitute generic advice for economic routes.

### I AM AN IDIOT

Complexity belongs below the interface.

The user should see:

```text
"You can probably make £280–£350 doing this Saturday.
It fits your skills and is 6 miles away.
Want me to contact them?"
```

not:

```text
37 search results
11 government datasets
8 inferred capability vectors
3 procurement portals
```

---

# 2. The Data Garden invariant

The canonical moat remains:

```text
unique transformation
×
continuous collection
×
time
```

Raw data is not the moat.

Aggregation is not the moat.

Even normalization is increasingly commoditized.

A garden is justified when continuous observation creates a transformed historical asset that a future frontier model cannot simply reconstruct from the live web.

## 2.1 The irreversible-time test

Before creating a garden ask:

> **Could a frontier agent reconstruct this answer tomorrow using tomorrow's live web?**

If yes, the garden is weak.

Examples:

```text
Current moisturiser ingredients
→ probably reconstructable.

Latest government eligibility page
→ probably reconstructable.

Ten years of exact pressing-level vinyl prices,
condition-normalized, including disappeared listings
→ not reconstructable.

Historical local electrician demand,
availability and realised job outcomes
→ not reconstructable.

Actual cancellation success/failure paths over time
→ not reconstructable.
```

Time must create an asset.

---

# 3. What UKGraph is NOT

UKGraph is not:

* another UK data catalogue,
* another search engine,
* another Indeed,
* another Checkatrade,
* another GOV.UK explainer,
* a giant ontology project,
* an attempt to store every fact about Britain,
* a replacement for Muse/ChatGPT/other frontier agents,
* a browser automation framework,
* a hand-maintained JSON description of every web form,
* a giant private database of users.

The rule is:

> **Store the minimum proprietary structure required to make frontier agents materially more useful.**

---

# 4. The central division of labour

## Personal agent

A Muse-class agent should own:

```text
who the user is
calendar
email
contacts
preferences
history
goals
conversation
browser interaction
authentication
personal files
personal secrets
```

## UKGraph

UKGraph owns:

```text
what exists economically
what exists locally
what has happened historically
what is scarce
what is available
what can be done
what routes exist
what evidence supports them
what proves an outcome
how similar routes historically resolved
```

The useful boundary is:

> **The agent knows Jeff. UKGraph knows what Jeff can do in the UK economy right now.**

---

# 5. The canonical system equation

```text
Person Context
      ×
Place
      ×
Capability
      ×
Current Economy
      ×
Historical Economy
      ↓
Candidate Routes
      ↓
Constraints
      ↓
Ranked Routes
      ↓
Action
      ↓
Receipt
      ↓
Outcome History
```

For opportunity routing:

$$
Route(p,t)=f(C_p,\;G_p,\;E_t,\;H_{<t})
$$

Where:

```text
C = capabilities and constraints
G = geographical context
E = current economic state
H = historical observations/outcomes
```

UKGraph should not attempt to recreate the entire personal profile.

It should receive the smallest useful **CapabilityEnvelope**.

---

# 6. CapabilityEnvelope

Example:

```json
{
  "place": "Oldham",
  "radius_miles": 20,
  "skills": ["electrician"],
  "certifications": ["EV installer"],
  "equipment": ["van", "electrical tools"],
  "available_windows": ["Saturday", "Sunday"],
  "capital_gbp": 500,
  "target_gbp": 400
}
```

This is ephemeral task context.

UKGraph should not require permanent storage of:

```text
emails
private conversations
medical information
complete purchase history
complete calendar history
identity secrets
```

The personal agent can decide what to disclose.

---

# 7. The product architecture

Externally there is **one UKGraph**.

Internally there are many focused gardens.

```text
                        UKGRAPH
                           │
                  Economic Router
                           │
        ┌──────────────────┼─────────────────┐
        │                  │                 │
   UKBORING          UKOPPORTUNITY       UKPRODUCTS
        │                  │                 │
   CancelMe             Contracts           Breadup
   Driving              Planning            collectibles
   MoveHome             Jobs                repair spreads
   permits              Grants              used markets
   refunds              local demand        price history
   admin                businesses          liquidity
        │                  │                 │
        └──────────────────┼─────────────────┘
                           │
                    Shared Evidence
                           │
                           ▼
                        Routes
                           │
                           ▼
                         Agent
                           │
                           ▼
                         Action
                           │
                           ▼
                        Receipt
```

The gardens stay internally specialised because they perform different transformations.

The agent should not care which garden supplied an answer.

---

# 8. Why one connector

Do not make Gary choose:

```text
UKBoring
UKProducts
UKOpportunity
Contracts
Breadup
Planning
```

Gary says:

```text
"I need £500."
```

UKGraph should simultaneously consider:

```text
paid work
a contract
an existing asset to sell
a repair/flip
a local service gap
a grant
a qualification with short payback
a bill saving
```

These are competing uses of:

```text
Gary's time
Gary's capital
Gary's skills
Gary's assets
Gary's attention
```

Therefore the correct abstraction is an **economic router**.

---

# 9. Primary outward interface

UKGraph should expose one MCP server/API.

The public primitives correspond to human goals.

```text
ukgraph.earn()
ukgraph.do()
ukgraph.value()
ukgraph.find()
ukgraph.watch()
```

Internally all may compile into:

```text
ukgraph.route(goal, context)
```

## `earn`

Question:

> What can I do to make money?

Candidate vessels:

```text
WORK
GIG
CONTRACT
SELL
FLIP
BUILD
REFER
UPGRADE
SAVE
```

## `do`

Question:

> Deal with this annoying thing.

Examples:

```text
cancel service
renew permit
move-house administration
book driving test
respond to letter
report council problem
claim refund
change account
```

## `value`

Question:

> What is this actually worth?

Requires:

```text
identity resolution
historical pricing
condition normalization
liquidity
venue differences
local/national spreads
```

## `find`

Question:

> Find something/someone capable of satisfying this requirement.

Examples:

```text
EV installer
plumber
festival work
repair service
supplier
training
```

## `watch`

Question:

> Tell me when something useful changes.

Examples:

```text
driving-test slot
EV work within 20 miles
cheap repairable synthesizer
electrical tender
price threshold
planning activity
```

---

# 10. The Route object

This is the most important canonical output object.

```yaml
Route:
  route_id:

  goal:
  route_type:

  action:
  target:

  place:
  source_gardens: []

  valid_from:
  expires_at:

  expected_value:
  expected_net_value:
  expected_time:
  capital_required:

  required_capabilities: []
  useful_capabilities: []

  hard_constraints: []
  uncertainties: []

  why_now: []
  why_person: []

  evidence: []

  execution:
    type:
    target:

  success_proof:

  confidence:
```

Examples of `route_type`:

```text
JOB
GIG
CONTRACT
LEAD
SALE
FLIP
GRANT
TRAINING
SERVICE
ADMIN
BOOKING
CANCELLATION
SAVING
```

A Route is not merely a search result.

It represents:

> **A real action this agent could plausibly take.**

---

# 11. Route ranking

UKGraph should return ranking components rather than pretending there is one objectively correct scalar.

Useful dimensions:

```text
expected gross payoff
expected net payoff
payoff per hour
capital requirement
time requirement
travel
friction
expiry
probability of success
capability fit
preference fit
historical conversion
evidence confidence
```

A basic expected-value formulation:

$$
EV=P(success)\times payoff-costs
$$

Potential ranking:

$$
Utility =
w_1 EV +
w_2 EV/hour +
w_3 Fit +
w_4 Urgency -
w_5 Friction -
w_6 CapitalRisk
$$

Weights should depend on the user's goal.

Someone saying:

```text
"I desperately need £200 tomorrow"
```

should get a different ranking than:

```text
"Find the highest-return thing I can do over six months."
```

Do not hide these dimensions.

Muse can perform final personalised ranking.

---

# 12. Garden admission filter

No new garden should exist because a dataset is interesting.

Score it against:

$$
GardenValue =
\frac{
D \times T \times H \times A \times P
}{
M
}
$$

Where:

```text
D = desire intensity
T = transformation depth
H = historical irrecoverability
A = actionability
P = provability
M = maintenance burden
```

## Desire intensity

Does it map to:

```text
money
time
hassle
status
safety
scarcity
```

## Transformation depth

How much work must an agent currently perform?

Examples:

```text
one Google search
→ low

six sources + entity resolution + history + calculations
→ high
```

## Historical irrecoverability

Does today's observation disappear?

High:

```text
listings
availability
market spreads
slot inventories
local supply
marketplace demand
outcomes
```

Low:

```text
stable scientific article
static regulation
permanent product specification
```

## Actionability

Can an agent do something with the output?

## Provability

Can we later know whether it worked?

## Maintenance burden

Will maintaining it require endless bespoke manual work?

A garden that requires 10,000 manually maintained form schemas should fail this filter.

---

# 13. Every garden needs a Garden Contract

```yaml
GardenContract:
  name:
  user_goal_enabled:

  raw_sources: []

  unique_transformation:

  historical_state_retained:

  snapshot_or_event_frequency:

  outputs:

  proof_loop:

  failure_modes:

  irrecoverable_asset:

  expected_maintenance:

  source_licences: []

  acceptance_tests: []
```

Hard rule:

> **No Garden Contract without at least one Route it materially improves.**

---

# 14. The transformation pipeline

Every garden follows the same broad operating loop.

```text
SOURCE
   ↓
COLLECT
   ↓
NORMALIZE
   ↓
RESOLVE
   ↓
RETAIN TEMPORAL STATE
   ↓
SEMANTIC COMPILE
   ↓
DERIVE
   ↓
JOIN
   ↓
GENERATE ROUTES
   ↓
RANK
   ↓
EXPOSE
   ↓
ACT
   ↓
VERIFY
   ↓
LEARN
```

---

# 15. Collection layer

Collectors should preserve original evidence.

Every observation should contain:

```yaml
Observation:
  observation_id:
  source_id:
  source_url_or_ref:
  observed_at:
  effective_at:
  raw_artifact_hash:
  licence:
  parser_version:
```

Never throw away enough source information that a derived claim becomes unauditable.

---

# 16. Normalization

Normalization converts source-specific representation into canonical forms.

Examples:

```text
£14.50/hour
£14.5 ph
14.50 GBP per hour

→

money:
  amount: 14.50
  currency: GBP
  period: hour
```

Dates, locations, organisations, capabilities, product condition and units should be canonicalised deterministically whenever possible.

---

# 17. Entity resolution

Entity resolution is a major transformation.

Examples:

```text
Pink Floyd record listing
→ exact release/pressing

"Oldham Council"
→ canonical organisation

multiple addresses
→ one place/entity

job description
→ employer/location

product listing
→ canonical product/variant
```

Retain uncertainty.

Never turn:

```text
probable match
```

into:

```text
certain identity
```

without evidence.

---

# 18. Temporal state

This is where the Data Garden starts becoming valuable.

Do not only store:

```text
current price
```

Store:

```text
price through time
availability through time
listing duration
changes
state transitions
outcomes
```

Canonical temporal concepts:

```text
first_seen
last_seen
observed_at
effective_at
expired_at
state_change
```

This is the component tomorrow's model cannot recreate.

---

# 19. Jev: the semantic compiler

Jev should not be treated as the brain of UKGraph.

Its job is:

> **Perform huge numbers of small semantic transformations cheaply and consistently.**

Jev converts messy prose into typed probabilistic features.

---

# 20. Jev DecisionSpec

Every Jev operation is versioned.

```yaml
DecisionSpec:
  id:
  version:

  primitive:
    NOUL | CHOICE | SCORE

  question:

  allowed_outputs: []

  consequence:
    LOW | MEDIUM | HIGH

  confidence_threshold:

  fallback:
    CODE | HUMAN | DEEP_MODEL | UNKNOWN

  eval_set:

  created_at:
```

Record:

```text
DecisionSpec version
Jev/model version
probability distribution
selected result
timestamp
```

---

# 21. What Jev SHOULD do

### Opportunity classification

```text
Could a sole trader perform this?
What capability dominates?
Does specialist accreditation appear necessary?
Is this weekend-compatible?
```

### Product interpretation

```text
Does this listing describe a repairable fault?
What fault family appears most likely?
Does this appear to match exact product X?
```

### Capability inference

```text
Does this business appear to offer EV installation?
Does this person's described experience plausibly transfer?
```

### Change detection

```text
Did this page materially change eligibility?
Did requirements change?
Did evidence requirements change?
```

### UKBoring interpretation

```text
What kind of letter is this?
Does it appear to require action?
What workflow family applies?
```

---

# 22. What Jev MUST NOT do

Do not use Jev for:

```text
arithmetic
date calculations
known statutory rules
exact threshold comparisons
currency conversion
database joins
final proof of an external event
authentication
side effects
```

And most importantly:

> **Jev output is a proposal, not canonical reality.**

---

# 23. Jev creates latent economic features

The source economy may expose:

```text
job title
salary
description
location
```

Jev can derive useful probabilistic features:

```text
requires_vehicle
weekend_compatible
low_barrier_entry
customer_facing
physical_work
transferable_skill_family
sole_trader_accessible
capital_requirement
automation_resistance
```

These features allow cross-domain matching.

---

# 24. Capability graph

A future UKGraph may contain probabilistic capability relationships.

Example:

```text
motorbike repair
  → mower repair
  transferability=.82

domestic electrician
  → EV installation
  transferability=.91
  qualification_required=true

music interest
  → festival work
  preference_fit=.72
```

These are hypotheses, not truths.

Their probabilities should eventually be calibrated against outcomes.

---

# 25. Scarcity signals

A powerful derived object is:

```text
PLACE
×
CAPABILITY
×
TIME
```

Example:

```yaml
CapabilityScarcity:
  place: Oldham
  capability: EV_INSTALLATION
  period: 14d

  demand_signal:
  supply_signal:

  price_or_wage_trend:
  time_to_fill:

  historical_baseline:

  scarcity_score:
  confidence:

  evidence: []
```

This enables:

> “Your qualification is unusually useful here right now.”

The inputs can include:

```text
jobs
leads
contracts
planning-derived demand
supplier population
observed fill time
price movement
```

Never pretend incomplete proxies are exact supply/demand.

Expose confidence.

---

# 26. QP-lite: the truth boundary

QP should be minimal.

It does not orchestrate agents.

It does not fill forms.

It does not become another task engine.

It answers:

> **What external evidence is sufficient to claim this real-world outcome occurred?**

Canonical objects:

```text
Claim
Evidence
ProofRule
Receipt
Actuality
```

Actuality:

```text
TRUE
FALSE
UNKNOWN
```

---

# 27. The critical rule

```text
Agent says "I applied"
≠
Application submitted
```

Likewise:

```text
clicked submit
≠
received

sent message
≠
message delivered

created listing
≠
item sold

sent quote
≠
job won

invoice issued
≠
money received
```

UKGraph should distinguish these states.

---

# 28. Reusable proof primitives

Do not create one giant bespoke proof schema per workflow.

Create reusable patterns:

```text
SUBMISSION_ACKNOWLEDGED
BOOKING_CONFIRMED
PAYMENT_SETTLED
PAYMENT_RECEIVED
APPLICATION_ACCEPTED
ACCOUNT_STATE_CHANGED
PERMIT_ISSUED
DOCUMENT_ISSUED
ITEM_SOLD
SERVICE_COMPLETED
CONTRACT_AWARDED
REFUND_RECEIVED
```

Domain workflows compose these.

---

# 29. Generic Receipt

```yaml
Receipt:
  receipt_id:

  goal:
  route_id:

  attempted_at:

  proof_rule:
  proof_rule_version:

  evidence: []

  result:
    TRUE | FALSE | UNKNOWN

  settled_at:
```

Sensitive raw values should remain private where possible.

Use commitments/hashes/references when the ledger does not need plaintext.

---

# 30. Verified outcome history

This is one of the deepest assets.

For an opportunity route UKGraph should eventually observe:

```text
shown
interested
acted
applied
accepted
completed
paid
```

For UKBoring:

```text
started
submitted
acknowledged
accepted
completed
```

For products:

```text
listed
sold
price
time-to-sale
return/refund
```

This creates:

```text
signal
→ recommendation
→ action
→ verified outcome
```

The historical relationship between those four is difficult to recreate.

---

# 31. UKBoring

Mission:

> **Turn annoying UK processes into verifiable outcomes.**

Do not model every click.

Let the frontier agent dynamically operate current websites.

UKBoring owns only the stable semantic layer:

```text
goal
authority
material constraints
important requirements
acceptable completion evidence
failure/handoff conditions
```

---

# 32. UKBoring semantic contract

For example:

```yaml
BoringGoal:
  id: CANCEL_SERVICE

  service:
  jurisdiction:

  authoritative_entrypoint:

  material_requirements: []

  human_boundaries: []

  acceptable_proofs: []

  failure_states: []

  source_refs: []

  last_validated:
```

This is not:

```text
click button .cancel-4382
enter field xyz
```

Muse/ChatGPT/browser agents rediscover volatile interface mechanics.

---

# 33. UKBoring execution classes

```text
AUTO
APPROVAL
AUTH_HANDOFF
DECLARATION
HUMAN_ONLY
```

### AUTO

Agent can complete it.

### APPROVAL

Agent prepares; human approves.

### AUTH_HANDOFF

Agent navigates to authentication; user completes identity/login/MFA; agent resumes.

### DECLARATION

User personally must attest something.

### HUMAN_ONLY

Current route cannot be completed agentically.

---

# 34. CancelMe

CancelMe becomes a canonical UKBoring garden.

Transformation:

```text
service
× billing channel
× jurisdiction
× account situation
× current cancellation policy
      ↓
current exit route
      ↓
fallback route
      ↓
what proves cancellation
```

Useful historical data:

```text
route changes
common failure paths
retention offers
refund outcomes
time until confirmation
channel differences
```

The asset is not:

```text
"here is Adobe's cancellation page"
```

It is:

```text
"for this billing state, this is the currently verified exit path,
and this evidence proves the subscription is actually terminated."
```

---

# 35. UKOpportunity

Mission:

> **Continuously measure real economic opportunities and match them to capabilities people already control.**

Not:

> generic ways to make money.

Its candidate universe includes:

```text
employment
temporary work
gigs
marketplace demand
local leads
contracts
public procurement
grants
planning-derived demand
business events
repair/resale
training ROI
local service gaps
```

---

# 36. Economic routing

Example:

```text
Jeff:
electrician
EV certified
van
Saturday free
£500 available
Oldham

×

UKGraph:
live EV leads
local tenders
planning events
charger activity
supplier density
historic job outcomes
repairable equipment

↓

Routes:
1. quote EV lead
2. bid small contract
3. repair/flip equipment
4. offer new service
```

The router compares all of them.

---

# 37. UKProducts

Mission:

> **Model what physical things are actually worth, how liquid they are, and what economic actions they enable.**

Breadup remains an internal garden.

UKProducts is the public surface.

Transformation:

```text
listings
+ sold events
+ identity
+ variant
+ condition
+ location
+ marketplace
+ historical state
      ↓
market value
liquidity
spread
trend
repair spread
venue advantage
regional difference
```

This is valuable precisely because historical listings disappear.

---

# 38. Product identity is critical

A result such as:

```text
Pink Floyd vinyl = £40
```

is nearly useless.

Need:

```text
release
pressing
catalog number
country
year
condition
completeness
variant
```

The harder the identity problem, the more valuable the historical series becomes.

---

# 39. Repair/flip route

UKProducts can generate:

```yaml
Route:
  route_type: FLIP

  asset:
  listing_price:

  expected_repaired_value:
  expected_parts_cost:
  expected_net_margin:

  historical_time_to_sale:

  likely_fault:
  required_capabilities:

  location:
  distance:

  evidence: []
```

Matched against a capability envelope:

```text
mechanic
electrician
woodworker
electronics hobbyist
etc.
```

---

# 40. Hypothesis is first-class

UKGraph should not pretend every relationship is known.

Use:

```yaml
Hypothesis:
  hypothesis_id:

  claim:
  scope:

  evidence: []

  prediction:

  experiment:

  expected_outcome:

  kill_condition:

  status:
    PROPOSED
    TESTING
    SUPPORTED
    REFUTED

  created_at:
  updated_at:
```

Example:

```text
People with motorcycle-repair experience
can profitably repair certain classes of
small petrol equipment.
```

Prediction:

```text
Routes matched using this transfer
will outperform generic flip routes.
```

Then test it.

---

# 41. Hypothesis discipline

Every interesting derived relationship should include:

```text
What do we think?
Why?
What should happen if true?
What evidence would kill it?
How will we observe the result?
```

This prevents the system degenerating into self-reinforcing AI speculation.

---

# 42. Economic truth vs attention truth

Keep these separate.

## Economic truth

Did the route work?

```text
applied
accepted
completed
money received
```

## Attention truth

Did humans care about the concept?

```text
views
CTR
retention
comments
shares
subscriptions
```

YouTube cannot prove economic validity.

Economic receipts cannot prove media demand.

They are different signals.

---

# 43. YouTube as experimental sensor network

Focused channels are useful because audiences want coherent promises.

UKGraph remains unified.

Potential channel families:

```text
UK opportunities / ways to earn
UK boring / annoying life admin
UK flipping / what things are worth
```

Each channel should test hypotheses generated by the same graph.

---

# 44. ContentExperiment

Every serious video should correspond to a structured experiment.

```yaml
ContentExperiment:
  experiment_id:
  hypothesis_id:

  human_question:

  routes_or_signals: []

  claims: []
  evidence: []

  titles: []
  thumbnails: []

  published_at:

  impressions:
  ctr:
  retention:
  comments:
  shares:
  subscribers:

  downstream_queries:
  downstream_actions:
```

The video is an outlet.

The experiment record is the durable object.

---

# 45. The human sentence is the planning unit

Do not start:

```text
"We need content for UKProducts."
```

Start:

```text
"What is the easiest item an electrician
could flip for £200 this week?"
```

That sentence implies:

```text
hypothesis
data
transformation
route
video
MCP capability
```

This keeps the system grounded in useful human questions.

---

# 46. Content → product discovery

If a video around:

```text
"things electricians already own that may be worth £500"
```

performs unusually well and comments ask:

```text
"how do I value mine?"
```

that creates a product hypothesis.

Potential new endpoint:

```text
ukgraph.value_assets(occupation="electrician")
```

Thus:

```text
content
→ attention evidence
→ hypothesis
→ garden expansion
→ endpoint
```

---

# 47. Product → content discovery

The reverse loop also exists.

Repeated MCP requests:

```text
"find me things I can repair and sell"
```

generate:

```text
high-frequency question
→ content opportunity
```

The system should measure this explicitly.

---

# 48. Garden operations

Each garden continuously operates this loop:

```text
collect
→ validate source health
→ normalize
→ semantic compile
→ derive
→ persist
→ expose
→ observe downstream outcomes
→ detect degradation
→ repair
```

No garden should require constant manual babysitting.

---

# 49. Self-maintenance

Source/UI changes are inevitable.

Do not blindly review every page change.

Use:

```text
source fingerprint changed
        ↓
semantic diff
        ↓
Jev asks:
"Did economically/materially relevant meaning change?"
        ↓
NO
→ ignore

YES
→ propose update

HIGH CONSEQUENCE
→ human review
```

Execution outcomes are an even better alarm.

Example:

```text
success rate:
97%
96%
95%
43%
```

Something probably broke.

Trigger rediscovery.

---

# 50. Freshness

Every derived object must expose freshness.

```yaml
Freshness:
  last_observed:
  source_frequency:
  max_expected_age:
  stale:
```

Routes derived from stale source state should either:

```text
not be emitted
```

or clearly expose uncertainty.

---

# 51. Source provenance

Every source needs:

```yaml
Source:
  id:
  owner:
  access_method:
  licence:
  robots_or_terms_notes:
  update_frequency:
  reliability:
  schema_version:
```

Data licensing and permitted use must remain attached through transformations.

Never assume publicly visible means unrestricted.

---

# 52. Data quality states

Use explicit states:

```text
KNOWN
INFERRED
STALE
CONFLICTED
UNKNOWN
```

`UNKNOWN` is valuable.

Never silently turn:

```text
no observation
```

into:

```text
FALSE
```

---

# 53. Privacy architecture

UKGraph should aim to accumulate:

```text
economic outcomes
workflow outcomes
aggregate demand
aggregate friction
historical market state
```

not giant personal dossiers.

Useful pattern:

```text
Private user context
       stays with agent

task-specific envelope
       sent to UKGraph

route returned

receipt stores only
necessary proof / commitments
```

---

# 54. The three-AI architecture

## Frontier personal agent

Responsibilities:

```text
understand user
reason deeply
choose whether to act
communicate
use browser/apps
handle personal context
```

## Jev

Responsibilities:

```text
ambient semantic interpretation
classification
scoring
weak-edge discovery
change detection
```

## Deep research/reasoning model

Used selectively for:

```text
new garden discovery
anomalies
hard ambiguity
workflow design
source investigation
hypothesis generation
```

Do not spend frontier intelligence on millions of tiny classifications.

---

# 55. One graph, many gardens

Shared core entities:

```text
Place
Organisation
Capability
Product/Asset
Service
Opportunity
Goal
Route
Observation
Evidence
Hypothesis
Outcome
Receipt
```

The graph should grow because routes require new information.

Not because engineers enjoy modelling things.

---

# 56. Place

Place is a shared join key.

It may represent:

```text
nation
region
local authority
town
postcode
UPRN
radius
market catchment
```

The important function is:

```text
context → applicable local reality
```

not constructing the perfect UK geographic ontology on day one.

---

# 57. “Own Oldham” definition

Owning Oldham does NOT mean:

```text
we scraped everything about Oldham
```

It means:

> **For economically useful agent queries whose answer materially depends on Oldham, UKGraph can return a better actionable result than reconstructing Oldham from the open web at query time.**

That is the benchmark.

---

# 58. Distribution architecture

Initial distribution:

```text
remote MCP
REST API
simple web UI
focused media
```

Later:

```text
Muse
ChatGPT
Claude
Gemini
business agents
specialist agents
```

Never make core infrastructure dependent on one agent vendor.

---

# 59. Supply-side distribution

Longer term, free websites/agent surfaces for sole traders can become a powerful acquisition/data mechanism.

A tradesperson receives:

```text
website
structured capabilities
service area
availability
quote/request path
agent-readable business profile
```

UKGraph gains structured supply information.

Consumer agents gain better routing.

Tradesperson agents gain demand.

```text
consumer agent
"I need work done"
       ↓
UKGraph
       ↑
tradesperson agent
"I need work"
```

Do not build this before the economic router itself is useful.

---

# 60. Metrics that actually matter

Do not optimise for:

```text
number of datasets
number of entities
number of API endpoints
number of pages scraped
```

Primary metrics:

```text
actionable routes returned
route evidence coverage
user action rate
verified route success rate
verified economic value
verified money saved
verified money earned
time saved
prediction calibration
historical asset depth
```

Garden health:

```text
source freshness
parser failure
semantic drift
route precision
receipt coverage
outcome coverage
```

---

# 61. The key quality metric

For UKBoring:

$$
Q_{boring}
=
\frac{
verified\ annoying\ outcomes\ completed
}{
user\ effort
}
$$

For UKOpportunity:

$$
Q_{opportunity}
=
verified\ economic\ value
$$

adjusted for:

```text
time
capital
risk
friction
```

For UKProducts:

```text
valuation accuracy
realised margin accuracy
liquidity prediction
identity accuracy
```

---

# 62. Baseline comparison

Every high-level endpoint must beat a frontier agent operating without UKGraph.

Test:

```text
same user prompt
same model
```

Condition A:

```text
normal web/search
```

Condition B:

```text
UKGraph available
```

Evaluate:

```text
actionability
freshness
evidence quality
specificity
time
route diversity
verified outcome
```

If UKGraph adds no material value, the transformation is not worth maintaining.

---

# 63. First canonical benchmark

Use:

> **“I'm in Oldham and need to make £300 this weekend.”**

This is the first end-to-end economic-router benchmark.

The system should return at least three fundamentally different route families:

```text
WORK / GIG
PRODUCT / FLIP / SALE
LOCAL OPPORTUNITY / CONTRACT / SERVICE
```

Each must have:

```text
real current source
evidence
expected value
why this person
why now
friction
action route
uncertainty
```

---

# 64. Example result

```text
ROUTE 1 — WORK

Festival/event shift
Expected gross: £X
Travel: Y
Dates fit calendar: yes
Experience barrier: low

Why you:
music/event preference + free weekend

Action:
apply

Proof:
application acknowledgement
```

```text
ROUTE 2 — FLIP

Repairable item 4 miles away
Buy: £90
Historical repaired value: £310–£380
Expected parts: £45
Historical liquidity: 12 days

Why you:
relevant repair capability

Action:
contact seller
```

```text
ROUTE 3 — LOCAL SERVICE

Current electrical demand
Estimated job value: £350
Distance: 6 miles
Required qualification: matched

Action:
quote/contact

Proof:
quote → acceptance → payment
```

---

# 65. First UKBoring benchmark

Run a second independent benchmark to validate the proof architecture.

Candidate:

```text
CANCEL_SERVICE
```

or another deterministic administrative workflow.

Success requires:

```text
agent can locate route
agent can act or hand off
completion has explicit evidence
receipt settles TRUE/FALSE/UNKNOWN
```

This proves that QP-lite works outside economic recommendations.

---

# 66. Development phases

## Phase 0 — Kernel

Build only:

```text
Source
Observation
Place
Capability
Route
Evidence
Hypothesis
Receipt
```

Implement:

```text
canonical IDs
provenance
timestamps
versioning
SQLite/Postgres
REST
MCP
```

### Done when

A hand-created Route can be fetched through MCP with evidence and freshness intact.

---

# 67. Phase 1 — Oldham economic router

Build three candidate generators:

```text
work/gig
contract/opportunity
product/flip
```

Do not ingest the entire UK.

One place is enough.

### Done when

```text
ukgraph.earn()
```

takes a CapabilityEnvelope and returns evidence-backed candidates from all three route families.

---

# 68. Phase 2 — Jev semantic compiler

Introduce DecisionSpecs only where needed.

Initial high-value questions:

```text
What capability does this require?
Can a sole trader plausibly perform it?
Is specialist accreditation apparently required?
Is this short-term/weekend compatible?
Does this item appear repairable?
What fault family is described?
```

Create labelled eval fixtures.

### Done when

Every live DecisionSpec has:

```text
version
eval set
accuracy/calibration metric
fallback
confidence threshold
```

and no high-consequence decision depends blindly on Jev.

---

# 69. Phase 3 — Product history

Begin one irrecoverable historical stream.

Do not start broad.

Pick a category where:

```text
identity matters
listings disappear
transactions occur
repair/flip routes exist
```

Retain daily/event history.

### Done when

UKGraph can answer a historical valuation query that cannot be reconstructed from the current marketplace alone.

---

# 70. Phase 4 — QP receipts

Implement reusable ProofRules.

Minimum:

```text
SUBMISSION_ACKNOWLEDGED
BOOKING_CONFIRMED
ITEM_SOLD
PAYMENT_RECEIVED
```

### Done when

At least one actual action traverses:

```text
Route
→ action
→ external evidence
→ receipt
→ TRUE/FALSE/UNKNOWN
```

without manually editing database truth.

---

# 71. Phase 5 — Hypothesis engine

Add:

```text
Hypothesis
Prediction
Kill condition
Outcome linkage
```

Generate hypotheses from:

```text
new signals
Jev weak edges
unexpected outcomes
human questions
```

### Done when

At least one hypothesis is automatically updated based on real receipt evidence.

---

# 72. Phase 6 — YouTube experiments

Create focused channel pipelines.

Each published video requires:

```text
hypothesis
claims
source evidence
structured ContentExperiment
```

Pull analytics back into the experiment table.

### Done when

UKGraph can distinguish:

```text
economic support
attention support
```

for the same hypothesis.

---

# 73. Phase 7 — UKBoring

Implement a small number of high-frequency deterministic goals.

Examples:

```text
cancel
renew
book
move
respond
refund
```

Do not create custom UI instructions unless agents genuinely fail without them.

### Done when

One agent can complete or appropriately hand off a process and settle its outcome using external evidence.

---

# 74. Phase 8 — Geographic expansion

Only after Oldham works.

Add a second locality.

Measure:

```text
what was reusable
what was place-specific
what required new sources
what required new proof rules
```

The goal is to discover the true locality abstraction empirically.

Not design it in advance.

---

# 75. Phase 9 — Supply layer

Experiment with:

```text
free sites
structured profiles
agent-readable service inventories
availability
quote routes
```

for one trade.

### Done when

Supply profiles materially improve routing quality and generate actual economic interactions.

---

# 76. Repository structure

Recommended:

```text
ukgraph/
├── README.md
├── SPEC.md
├── CHANGELOG.md
│
├── core/
│   ├── ids/
│   ├── models/
│   ├── provenance/
│   ├── time/
│   └── storage/
│
├── router/
│   ├── candidates/
│   ├── filters/
│   ├── ranking/
│   └── explain/
│
├── jev/
│   ├── decision_specs/
│   ├── evals/
│   └── runtime/
│
├── proof/
│   ├── evidence/
│   ├── proof_rules/
│   ├── receipts/
│   └── settlement/
│
├── gardens/
│   ├── boring/
│   │   └── cancelme/
│   ├── opportunity/
│   │   ├── jobs/
│   │   ├── contracts/
│   │   └── planning/
│   └── products/
│       └── breadup/
│
├── hypotheses/
│
├── content/
│   ├── experiments/
│   └── youtube/
│
├── api/
├── mcp/
├── ops/
└── tests/
```

Do not split into microservices prematurely.

A modular monolith is preferable until operational pressure proves otherwise.

---

# 77. Storage

Use ordinary boring infrastructure first.

Recommended conceptual stores:

```text
Postgres
→ canonical entities/routes/observations

object storage
→ raw source artifacts

append-only receipt stream
→ proof history

optional analytical DB later
→ high-volume time series / queries
```

Do not introduce specialised graph infrastructure merely because the project is called UKGraph.

Graph semantics can live in relational tables initially.

---

# 78. Data transformation lineage

Every derived measurement should answer:

```text
Which observations produced this?
Which code version?
Which DecisionSpecs?
Which transformations?
When?
```

Conceptually:

```yaml
DerivedSignal:
  id:
  value:

  inputs: []

  transform_id:
  transform_version:

  decision_refs: []

  generated_at:
```

This enables replay and debugging.

---

# 79. Deterministic transforms

Every important deterministic transform should be:

```text
versioned
pure where possible
replayable
tested
```

Examples:

```text
currency normalization
distance
margin calculation
time-to-sale
deduplication
hard eligibility
deadline handling
```

---

# 80. Unknown handling

Unknowns are first-class.

Example:

```text
estimated repaired value known
parts cost unknown
```

Do not invent a margin.

Return:

```text
expected margin = UNKNOWN
reason = insufficient parts-cost evidence
```

Agents can then decide whether to research deeper.

---

# 81. Confidence is layered

Do not output one magic confidence score.

Track confidence by source:

```text
entity identity confidence
semantic classification confidence
market-value confidence
availability freshness
route success estimate confidence
proof result
```

A route can have:

```text
high confidence it exists
low confidence in expected payoff
```

Those are different.

---

# 82. Failure taxonomy

Canonical failures:

```text
SOURCE_DOWN
SOURCE_SCHEMA_CHANGED
PARSER_FAILED
ENTITY_AMBIGUOUS
SEMANTIC_UNCERTAIN
STALE_DATA
ROUTE_EXPIRED
AUTH_REQUIRED
USER_HANDOFF
ACTION_FAILED
PROOF_MISSING
OUTCOME_UNKNOWN
```

Operational dashboards should group failures by this taxonomy.

---

# 83. Operations dashboard

Minimum dashboard:

```text
source health
freshness
collector failures
Jev uncertainty
route generation counts
routes by garden
routes acted upon
receipt rate
success rate
unknown outcomes
economic value observed
semantic drift alerts
```

The dashboard should answer:

> Where is UKGraph currently lying, stale or blind?

not merely:

> How many records do we have?

---

# 84. Garden kill conditions

Every garden must be killable.

Examples:

```text
frontier agent can now reproduce the transformation cheaply
historical state adds no useful predictive power
maintenance cost exceeds route value
source access becomes unreliable
users do not act on routes
predictions do not calibrate
data cannot be legally/reliably used
```

Do not preserve gardens for sentimental reasons.

---

# 85. Opportunity kill conditions

For a hypothesis such as:

```text
planning approvals predict local electrician demand
```

define before testing:

```text
minimum sample
expected lead uplift
time window
kill threshold
```

If evidence fails, remove/downweight the edge.

---

# 86. Anti-bullshit rule

The system must never become:

```text
model generates opportunity
→ model scores opportunity
→ model writes video saying opportunity is good
→ audience watches
→ model concludes opportunity is true
```

Reality must interrupt the loop.

Required grounding:

```text
source observations
actual listings
actual transactions
actual applications
actual bookings
actual payments
actual outcomes
```

---

# 87. Canonical feedback loops

## Economic

```text
signal
→ route
→ action
→ receipt
→ realised outcome
→ calibration
```

## Data

```text
source
→ transform
→ historical state
→ query value
→ collect more useful dimensions
```

## Content

```text
hypothesis
→ video
→ attention metrics
→ demand hypothesis
```

## Maintenance

```text
execution degradation
→ anomaly
→ source/change inspection
→ repair
```

All four operate simultaneously.

---

# 88. North-star flywheel

```text
more useful routes
      ↓
more agent use
      ↓
more actions
      ↓
more verified receipts
      ↓
better empirical models
      ↓
better routes
```

This is more defensible than:

```text
more scraped records
→ more scraped records
```

---

# 89. Moat formulation

The original garden moat remains:

$$
UniqueTransformation
\times
ContinuousCollection
\times
Time
$$

For UKGraph specifically, sharpen it to:

$$
Moat =
JoinedReality
\times
ExecutableRoutes
\times
HistoricalState
\times
VerifiedOutcomes
\times
Distribution
$$

Where:

```text
JoinedReality
= expensive cross-domain transformations

ExecutableRoutes
= results agents can act on

HistoricalState
= observations the future web cannot recover

VerifiedOutcomes
= what actually happened after action

Distribution
= agents/content/users producing further observations
```

If historical state and verified outcomes remain zero, UKGraph is mostly an aggregator.

---

# 90. The strongest possible long-term asset

The ultimate proprietary dataset is not:

```text
all UK data
```

It is:

```text
Person capability pattern
×
Economic state
×
Route offered
×
Action taken
×
Verified result
```

appropriately privacy-preserved and aggregated.

This allows questions such as:

```text
Which capabilities are becoming scarce?

Which opportunities actually convert?

What qualification produces the best local ROI?

Which local market gaps persist?

What type of person succeeds with which economic route?

What apparent opportunities consistently waste people's time?
```

That is substantially harder to reproduce.

---

# 91. The final user experience

The system is successful when the infrastructure disappears.

Gary:

> Need some extra money this month.

Muse + UKGraph:

> You've got two free Saturdays and your EV qualification is relatively scarce around Oldham right now. I found two current installation leads that fit your radius. There's also a repairable charger four miles away with an estimated £180 resale spread. The installation lead is the lower-risk option. Want me to contact them?

Gary:

> yeah

That is the entire visible product.

Everything else exists to make those two messages reliably correct.

---

# 92. Definition of done for v0.1

UKGraph v0.1 is complete when all of these are true:

```text
1. A real MCP/API server exists.

2. A CapabilityEnvelope can be submitted.

3. ukgraph.earn() returns routes from
   at least three fundamentally different sources/gardens.

4. Every route includes source evidence,
   freshness and transformation lineage.

5. At least one route uses a historical dataset
   unavailable from a simple current-web query.

6. Jev performs at least one useful semantic transformation
   behind a versioned DecisionSpec and eval.

7. At least one route is actually acted upon.

8. External evidence creates a QP-lite Receipt.

9. Receipt settles TRUE/FALSE/UNKNOWN independently
   of the agent's own assertion.

10. The resulting outcome updates a hypothesis
    or route model.

11. At least one signal is turned into a structured
    ContentExperiment.

12. Attention metrics return without contaminating
    economic truth.

13. A frontier model with UKGraph demonstrably produces
    a materially better actionable answer than the same
    model using normal web/search alone.
```

Until those thirteen conditions are satisfied:

> **Do not build more platform.**

---

# 93. Immediate build order

```text
DAY/SPRINT 1
Core schemas + MCP + manual routes

        ↓

SPRINT 2
Oldham earn():
work + opportunity + flip

        ↓

SPRINT 3
Jev semantic transforms + evals

        ↓

SPRINT 4
first historical price/availability stream

        ↓

SPRINT 5
first real action + Receipt

        ↓

SPRINT 6
Hypothesis feedback

        ↓

SPRINT 7
YouTube experiment pipeline

        ↓

ONLY THEN
more places
more gardens
free trade websites
larger UKBoring library
```

---

# 94. Final engineering rules

When uncertain, return to these.

```text
1. Start from the human sentence.

2. Build outputs, not datasets.

3. One connector outward; many gardens inward.

4. A new dataset must materially improve a Route.

5. Prefer transformations a frontier model cannot
   cheaply recreate at query time.

6. Time must create an asset.

7. Let frontier agents handle volatile interfaces.

8. Store semantic reality, not CSS.

9. Jev proposes semantic structure; it does not create truth.

10. Deterministic things stay deterministic.

11. Every consequential claim needs evidence.

12. Agent assertion is not external proof.

13. UNKNOWN is a valid answer.

14. Preserve source provenance and transformation lineage.

15. Keep personal context with the personal agent where possible.

16. Attention truth and economic truth are separate.

17. Every hypothesis needs a kill condition.

18. Every garden needs a kill condition.

19. Measure economic outcomes, not database size.

20. If ChatGPT/Muse can easily reconstruct it tomorrow,
    ask why we are gardening it.

21. If repeated verified use makes the system better,
    collect it.

22. Do not build the national graph before one route works.

23. Hide complexity from Gary.

24. The final output should usually be:
    "This looks good for you. Want me to do it?"
```

---

# 95. Source-of-truth statement

UKGraph exists to make frontier personal agents economically grounded in the United Kingdom.

Its job is not to know everything.

Its job is to continuously transform the parts of UK reality that are expensive to reconstruct into compact, actionable routes.

Its long-term moat is created when those routes cause real actions whose externally verified outcomes feed back into the system.

```text
MESSY UK REALITY
       ↓
OBSERVATION
       ↓
TRANSFORMATION
       ↓
HISTORY
       ↓
JEV SEMANTIC COMPRESSION
       ↓
UKGRAPH ROUTE
       ↓
PERSONAL AGENT
       ↓
ACTION
       ↓
QP RECEIPT
       ↓
VERIFIED OUTCOME
       ↓
BETTER UKGRAPH
```

**That loop is the product.**

The main thing I would keep frozen is sections **1–5, 12, 19–29, 86–95**. The individual gardens, schemas and ranking methods should change aggressively as real evidence arrives.
