<!-- STALE: This document describes an earlier naming scheme or unimplemented concept. Preserved for context. Current architecture is in ukgraph_final.md and SPEC.md. -->
# Content Map — Forests × Children × Titles × Audiences

## The loop

```text
YouTube titles force end-state thinking
→ what data do we need?
→ what transformations create the moat?
→ collect over time
→ sell as API
→ analytics tell us what to focus on
→ autonomous
```

---

# BREADUP — Things

> "What is this thing worth?"

---

## Child: Marketplace Intelligence

### Titles
- "The second-hand products rising fastest in value"
- "What should you flip with £100?"
- "The products with the biggest eBay vs Facebook price gap"
- "The easiest used items to sell within 7 days"
- "The worst things to buy new"
- "The best products to buy used and resell later"
- "What's actually worth selling on Vinted vs eBay?"
- "The second-hand products nobody is listing but everyone wants"

### Metric
`sold_price / listing_price` by platform × category

### Audience
Resellers, side-hustlers, students, parents clearing houses, charity shop volunteers

### AGI risk
Medium — AI can price items but can't physically source/ship

---

## Child: Pricing Engine

### Titles
- "How to price anything for second-hand sale"
- "What should you actually accept on Facebook Marketplace?"
- "The offer you should never take (and the one you should)"
- "Why your listings aren't selling (pricing data says why)"
- "How long should you wait before dropping the price?"
- "Dynamic pricing for second-hand: what airlines know that you don't"

### Metric
`optimal_list_price` by item × platform × time_on_market

### Audience
Anyone selling anything second-hand

### AGI risk
Low — pricing advice requires current market data

---

## Child: Repair vs Sell As-Is

### Titles
- "Broken things that are worth more than working ones"
- "What should you repair if you can solder?"
- "Should you fix it or sell it broken? The data says..."
- "The repair that costs £8 but adds £120 in value"
- "Things you should NEVER repair (even if you can)"
- "The hidden value in your broken appliances"

### Metric
`repair_cost / value_uplift` by item × fault

### Audience
DIYers, repair café volunteers, eBay sellers, tool owners

### AGI risk
Low — physical repair can't be automated

---

## Child: Part-Out Economics

### Titles
- "Should you part this out or sell it whole?"
- "The camera worth £90 whole but £191 in parts"
- "Donor matching: buy two broken, make one working"
- "The items where parts are worth more than the whole"
- "How to find the right donor machine for your repair"

### Metric
`sum(parts_value) - sum(sell_through_cost) vs whole_value`

### Audience
Repair shops, eBay part sellers, workshop hobbyists

### AGI risk
Low — physical disassembly required

---

## Child: Liquidation Intelligence

### Titles
- "This closed café has £11k of equipment for £3.2k"
- "How to buy from failed businesses for profit"
- "The auction lots nobody is bidding on (but should be)"
- "Restaurant liquidation: what's actually worth buying?"
- "Office clearances: the hidden gold in corporate shutdowns"

### Metric
`breakup_value / lot_price` by auction type × category

### Audience
Entrepreneurs, resellers, restaurant equipment buyers, asset traders

### AGI risk
Low — physical inspection and transport needed

---

# ROOM — Markets

> "Where is there room for me?"

---

## Child: Business Gap

### Titles
- "Which UK towns are desperate for this service?"
- "The business nobody is starting but everyone needs"
- "This neighbourhood has 4× demand but zero supply"
- "The UK's most underserved service by postcode"
- "What business should you start in your town?"

### Metric
`demand_index / supply_index` by business_type × postcode

### Audience
Entrepreneurs, franchise buyers, career switchers, commercial landlords

### AGI risk
Medium — AI can identify gaps but can't run physical businesses

---

## Child: Trade Demand

### Titles
- "The trades with the most room left"
- "Don't retrain as a plumber — become THIS instead"
- "Heat pump installers: the trade with the biggest gap"
- "Which trade has the best demand/supply ratio in your area?"
- "The regulation quietly creating thousands of trade jobs"

### Metric
`demand / available_workers` by trade × region

### Audience
Career switchers, apprentices, existing tradespeople expanding

### AGI risk
Low — physical trade work can't be automated

---

## Child: Local Price Intelligence

### Titles
- "That £1,800 quote is 42% above fair price"
- "What boiler repair actually costs in your postcode"
- "The tradesmen charging double (and the data to prove it)"
- "How much should you pay for an EV charger installation?"
- "The services where prices are rising fastest"

### Metric
`quoted_price / fair_price` by service × postcode

### Audience
Homeowners, property managers, landlords, anyone getting work done

### AGI risk
Low — requires local physical knowledge

---

## Child: Replacement Wave

### Titles
- "These 2,800 heat pumps are about to fail"
- "The boiler replacement crunch coming to your town"
- "Which UK homes are entering the replacement window?"
- "Solar inverter failures: the wave nobody is preparing for"
- "The £40m equipment replacement wave nobody sees coming"

### Metric
`installed_base × failure_probability` by asset_type × location × age

### Audience
Installers, manufacturers, parts sellers, finance providers, insurers

### AGI risk
Low — physical installation required

---

## Child: Regulation Impact

### Titles
- "The new law creating a £120m compliance market"
- "27,000 restaurants need this inspection by September"
- "The regulation nobody is talking about (but should be)"
- "New building rules: who wins, who loses?"
- "The compliance requirement creating instant demand"

### Metric
`affected_entities × required_action / existing_suppliers`

### Audience
Founders, agencies, accountants, consultants, tradespeople

### AGI risk
Low — compliance requires human judgment + physical presence

---

## Child: Market Crowding

### Titles
- "The UK jobs getting crowded fastest"
- "This 'high-demand' job is already becoming overcrowded"
- "3 jobs where demand is rising but competition isn't"
- "The worst career retraining bet in the UK right now"
- "The industries where wages are rising faster than hiring"
- "How to tell if your market is饱和 before everyone else"

### Metric
`entrant_rate / demand_growth` by market × region

### Audience
Career switchers, business founders, investors, recruiters

### AGI risk
Medium — AI can identify crowding but can't change career decisions

---

# POWPOWPOW — Resources

> "Where should compute/capital flow?"

---

## Child: Compute Allocation

### Titles
- "Which network pays the most for your compute?"
- "The mining opportunity everyone is missing"
- "The most profitable hardware right now"
- "Which network is paying too much for security?"
- "Where should your GPU be working right now?"

### Metric
`revenue_per_unit_resource` by network × hardware × time

### Audience
Miners, GPU owners, crypto investors, hardware buyers

### AGI risk
Low — physical hardware allocation

---

## Child: Seesaw Economics

### Titles
- "Which miners are getting squeezed fastest?"
- "Where is hashrate moving before price?"
- "The resource premium nobody is tracking"
- "Why this coin's mining economics just broke"
- "The reflexive loop nobody sees (until it's too late)"

### Metric
`allocation_wedge` by network × time

### Audience
Crypto traders, miners, protocol researchers, investors

### AGI risk
Low — physical resource economics

---

## Child: Hardware Economics

### Titles
- "What should you mine with this GPU?"
- "The GPU that pays for itself fastest"
- "H100 vs 4090: which earns more right now?"
- "The hardware about to become obsolete"
- "Electricity cost: the number that makes or breaks mining"

### Metric
`net_revenue_per_day` by hardware × electricity_cost × network

### Audience
Miners, hardware buyers, datacenter operators

### AGI risk
Low — physical hardware decision

---

## Child: Constraint Migration

### Titles
- "The bottleneck just moved from GPUs to power"
- "Why datacenter capacity is the new limiting factor"
- "HBM shortage: who gets squeezed next?"
- "The supply chain constraint nobody is mapping"
- "Where is the physical bottleneck in AI right now?"

### Metric
`constraint_tightness` by resource_layer × time

### Audience
AI researchers, datacenter investors, hardware analysts, semiconductor investors

### AGI risk
Low — physical infrastructure reality

---

# Cross-Forest: AGI Impact

> "Who is most at risk? What is changing fastest?"

---

## Titles
- "The jobs AI is actually replacing (not the ones you think)"
- "Which UK industries have the most automatable tasks?"
- "The services that cost £500 that AI now does for £50"
- "Who is most at risk from AI in your postcode?"
- "The AI capability that just collapsed a market"
- "New AI model just made this job 10× cheaper"
- "The skills that are becoming worthless (and the ones that aren't)"
- "Which small businesses are most exposed to AI?"

### Metric
`ai_capability × task_composition × market_price` by industry × region

### Audience
Everyone. Career switchers, business owners, employees, students, investors

### AGI risk
High — this IS the AGI story

---

# Analytics → Focus

Titles that perform well tell us:

```text
high views + high retention
→ audience cares deeply
→ build deeper data here
→ more titles in this area

high views + low retention
→ title works but content doesn't deliver
→ fix the data/proof layer

low views + high retention
→ niche but loyal audience
→ good for API/customers
→ less YouTube priority

low views + low retention
→ wrong area or wrong framing
→ deprioritize or reframe
```

---

# The data → content → API pipeline

```text
TITLE (what people want to know)
    ↓
METRIC (exact measurement needed)
    ↓
TRANSFORMATION (what makes this hard to get)
    ↓
COLLECTOR (data pipeline)
    ↓
ANSWER (immediate, evidence-backed)
    ↓
VIDEO (YouTube)
    ↓
ANALYTICS (what performed)
    ↓
API (sell the metric)
    ↓
FEEDBACK (what else do they want to know?)
    ↓
NEW TITLE
```

Every metric we define for a video title becomes:

1. A data collector
2. A transformation pipeline
3. An API endpoint
4. A content series
5. A compounding dataset

The videos force us to think of end-states.

The end-states force us to build the data.

The data becomes the moat.

The moat becomes the API.

The API feeds the next video.
