# Capabilities — What Would Somebody Ask Their Agent?

## The rule

> Don't build a capability until we can write ten compelling natural-language requests for it.
> Don't heavily build it until a corresponding content question shows evidence that humans actually care.

## The loop

```text
QUESTION (fake Muse request)
    ↓
VIDEO TITLE (reverse-engineered)
    ↓
EXPERIMENT (publish Short)
    ↓
ATTENTION SIGNAL (CTR, retention, comments)
    ↓
IF WINNING → build capability
    ↓
MUSE + MCP TOOL (real agent usage)
    ↓
OUTCOME DATA
    ↓
NEW QUESTIONS
```

---

## BREADUP — "What is this thing worth?"

### Fake Muse requests

| # | What somebody asks | Capability underneath |
|---|---|---|
| 1 | "Is this Facebook Marketplace camera actually a bargain?" | `value_listing(item, platform, condition)` |
| 2 | "What should I offer this seller?" | `max_offer(item, target_margin)` |
| 3 | "What stuff around me could I flip this weekend?" | `find_flips(location, budget, time)` |
| 4 | "Is it worth repairing this or should I sell as-is?" | `repair_vs_sell(item, fault)` |
| 5 | "Which eBay categories have the biggest margins right now?" | `best_categories(min_margin)` |
| 6 | "I found a box of old synths at a car boot — what's in it worth?" | `value_lot(items[])` |
| 7 | "What's the cheapest place to buy a [item]?" | `cheapest_source(item, max_condition)` |
| 8 | "Should I part this out or sell whole?" | `part_out_economics(item)` |
| 9 | "How fast do these sell?" | `liquidity_score(item)` |
| 10 | "What's this worth in 6 months?" | `depreciation_forecast(item, horizon)` |

### Video titles (reversed)

| # | Title | Hypothesis |
|---|---|---|
| 1 | "Can AI Spot Undervalued Facebook Marketplace Listings?" | People want arbitrage. They believe deals exist but can't systematically find them. |
| 2 | "I Tracked 10,000 eBay Sales to Find What Actually Flips" | Proof that a dataset exists. Viewers want the edge. |
| 3 | "What Stuff Around You Could You Flip This Weekend?" | Directly actionable. Low barrier. Drives saves. |
| 4 | "Should You Repair It or Sell It Broken?" | Every person with a broken thing faces this. Universal question. |
| 5 | "The eBay Categories Nobody's Watching (But Make Money)" | Curiosity + money. Secret knowledge framing. |
| 6 | "What's In A Box Of Old Synths? We Valued Everything" | Unboxing + valuation. Dual hook. |
| 7 | "The Same Thing Costs 3x More on One Platform" | Price transparency gap. Outrage + utility. |
| 8 | "Part It Out or Sell Whole? The Math Might Surprise You" | Decision framework. People love being told the answer. |
| 9 | "Things That Sell in 24 Hours vs Things That Sit for Months" | Speed = money. Urgency framing. |
| 10 | "What's Your Gear Worth in 6 Months? We Predicted It" | Prediction hook. Time-stamped credibility. |

### Probe video to make first

**"Is This Facebook Marketplace Camera Actually a Bargain?"**

Steps:
1. Screenshot 5 actual Facebook Marketplace camera listings
2. Cross-reference with eBay sold data
3. Show the gap between asking price and real market value
4. Jev classifies: BUY / OFFER / WATCH / PASS
5. End screen: "Try it yourself — link in description"

This proves the capability exists. Comments write the API spec.

---

## UKGRAPH — "Is there room for me?"

### Fake Muse requests

| # | What somebody asks | Capability underneath |
|---|---|---|
| 1 | "What businesses are weirdly undersupplied around me?" | `find_local_constraints(postcode, sector)` |
| 2 | "What could I learn in 3 months that is scarce where I live?" | `find_skill_opportunities(postcode, budget)` |
| 3 | "Where in Britain are electricians getting unusually expensive?" | `compare_constraint_regions(skill)` |
| 4 | "Should I switch to cybersecurity?" | `evaluate_career_move(from_role, to_role)` |
| 5 | "Which UK trades have the best pay-to-training ratio?" | `trade_roi_ranking(region)` |
| 6 | "What's happening to jobs in my area?" | `local_job_trend(postcode)` |
| 7 | "Is there room to start a [business] in [city]?" | `market_gap(business_type, city)` |
| 8 | "Which new laws are creating new markets?" | `regulation_opportunities(date_range)` |
| 9 | "What jobs will AI create in the UK?" | `ai_created_roles(sector)` |
| 10 | "Where are wages rising fastest?" | `wage_growth_map(region, occupation)` |

### Video titles (reversed)

| # | Title | Hypothesis |
|---|---|---|
| 1 | "What Is Britain Running Out Of?" | Shortage framing. Everybody thinks their area is unique. National interest. |
| 2 | "The UK Skills That Pay Most in 3 Months" | Time-bounded. Specific. Directly actionable for career switchers. |
| 3 | "Why Electricians in Manchester Cost 40% More Than London" | Regional surprise. Counterintuitive. Strong hook. |
| 4 | "Is Your Job About to Get Crowded?" | Threat + curiosity. Personal stakes. |
| 5 | "The Trades Nobody's Talking About" | Secret knowledge. Underdog framing. |
| 6 | "What's Actually Happening to Jobs in [City]?" | Personalized format. Works for every city. Series potential. |
| 7 | "Is There Room for a [Business] in Your Town?" | Directly answers the founder question. Repeatable. |
| 8 | "The Laws Coming in 2027 That Will Make People Rich" | Regulation = opportunity. Forward-looking. Time pressure. |
| 9 | "The Jobs AI Is Creating (Not Destroying)" | Positive spin on AI anxiety. Differentiated angle. |
| 10 | "Where Wages Are Rising Fastest Right Now" | Pure utility. High save rate. |

### Probe video to make first

**"What Is Britain Running Out Of?"**

Steps:
1. Query ONS vacancies data + Companies House births/deaths
2. Find sectors where demand is up but supply (new companies + job ads) is flat or falling
3. Rank by gap size
4. Jev classifies: which regions, which trades, which severity
5. Show map of UK with colour-coded shortages

This proves the UKGraph capability. Comments ask "what about my city?" → that's the API spec.

---

## POWPOWPOW — "Where should my compute go?"

### Fake Muse requests

| # | What somebody asks | Capability underneath |
|---|---|---|
| 1 | "Can this gaming PC make me money overnight?" | `evaluate_hardware(hardware, electricity)` |
| 2 | "What should I mine with this GPU today?" | `find_compute_opportunity(hardware, electricity, risk)` |
| 3 | "Is it better to mine or rent out my GPUs?" | `mine_vs_rent(hardware, electricity)` |
| 4 | "Which network is about to pump?" | `emission_forecast(network)` |
| 5 | "What's the most profitable coin to mine right now?" | `profitability_ranking(hardware, electricity)` |
| 6 | "Should I sell my mining GPUs or keep going?" | `hold_vs_sell(hardware, electricity, trend)` |
| 7 | "How much would I make with 4x RTX 4090s?" | `portfolio_revenue(hardware[], electricity)` |
| 8 | "Which pools are safest?" | `pool_risk_assessment(network)` |
| 9 | "What happens to mining when Bitcoin halves?" | `halving_impact(network, horizon)` |
| 10 | "Where's the cheapest electricity for mining?" | `energy_arbitrage(location, power需求)` |

### Video titles (reversed)

| # | Title | Hypothesis |
|---|---|---|
| 1 | "Can Your Gaming PC Actually Make Money While You Sleep?" | Every gamer has thought this. Provable. Clickbait that delivers. |
| 2 | "We Tracked RTX 4090 Mining Profitability Every Hour for 90 Days" | Longitudinal = credibility. Time investment = moat. |
| 3 | "Mine or Rent? The Math Will Surprise You" | Decision framework. People love being told the answer. |
| 4 | "The Coin That's About to Get a Lot More Profitable" | Prediction. Forward-looking. Time pressure. |
| 5 | "The Most Profitable Coin to Mine Right Now (September 2026)" | Timestamped. Refreshable. Evergreen format. |
| 6 | "Should You Sell Your Mining GPUs or Ride It Out?" | Common dilemma. High stakes for miners. |
| 7 | "I Built a 4-GPU Mining Rig. Here's What It Makes." | Build + revenue reveal. Dual hook. |
| 8 | "Pool Hopping Is Costing You Money. Here's Why." | Problem → solution. Educational. |
| 9 | "What Bitcoin's Halving Does to Every Other Coin" | Systemic thinking. Interesting for investors too. |
| 10 | "The Cheapest Electricity in the World for Mining" | Geographic. Surprising data. Shareable. |

### Probe video to make first

**"Can Your Gaming PC Actually Make Money While You Sleep?"**

Steps:
1. Take 5 common GPU models (RTX 4060, 4070, 4080, 4090, RX 7900 XTX)
2. Run profitability calc across all 17 tracked networks
3. Show: some GPUs make £0.02/day, some make £3/day
4. Compare to electricity cost
5. End with: "The answer depends on your electricity price"
6. Jev classifies: which GPUs are profitable at which electricity tiers

This is thePowPowPow proof of concept. Comments ask "what about my specific GPU?" → capability spec.

---

## ROAST.PET — "Make Dad something ridiculous from his dog"

### Fake Muse requests

| # | What somebody asks | Capability underneath |
|---|---|---|
| 1 | "Roast my dog" | `create_pet_performance(photo, style)` |
| 2 | "Make a birthday card from my cat" | `create_gift_card(photo, occasion)` |
| 3 | "Turn my pet into a character" | `character_render(photo, art_style)` |
| 4 | "Write a roast of my friend's cooking" | `create_roast(target, style, intensity)` |
| 5 | "Make me a funny video about my commute" | `create_observation_video(topic, style)` |

### Video titles (reversed)

| # | Title |
|---|---|
| 1 | "We Roasted 100 Dogs. Here Are the Best." |
| 2 | "AI Turned My Cat Into a Fortune Teller" |
| 3 | "The Most Offensive Birthday Card Ever Made" |
| 4 | "We Made a Comedy Show From People's Pets" |
| 5 | "Your Dog Is Funnier Than You Think" |

### Probe video to make first

**"We Roasted 100 Dogs. Here Are the Best."**

Steps:
1. Collect 100 pet photos from roast.pet orders
2. Generate character portraits + roast lines
3. Compile into a "best of" video
4. Show the audience reaction (laughs, shares)
5. End: "Submit your pet for roasting — link in description"

---

## The capability-building sequence

For each garden, follow this order:

1. **Write 10 fake Muse requests** (what would somebody ask?)
2. **Reverse into 10 video titles** (what would somebody click?)
3. **Pick the best probe video** (highest hypothesis confidence)
4. **Publish it** (get real attention signal)
5. **Read comments** (what are people actually asking?)
6. **If winning → build the capability** (MCP tool + Muse connector)
7. **If losing → pivot** (try the next video title)

Don't build the API until the video proves people care.

---

## Priority order

| Priority | Probe video | Garden | Why first |
|----------|-------------|--------|-----------|
| 1 | "Can Your Gaming PC Make Money While You Sleep?" | PowPowPow | Has live data (17 chains). Most clickable. |
| 2 | "What Is Britain Running Out Of?" | UKGraph | Has ONS data. Broad appeal. |
| 3 | "Is This Marketplace Camera a Bargain?" | Breadup | Needs eBay data (run locally). Most personal. |
| 4 | "We Roasted 100 Dogs" | Roast.pet | Has existing orders. Viral potential. |
