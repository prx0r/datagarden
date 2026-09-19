# DataGarden — Muse Connector Submission

## Product Name
DataGarden — Economic Reality Engine

## Description
DataGarden gives Muse access to three live economic data forests:

1. **Breadup** — Physical goods valuation. "What's this worth?" / "Should I buy this?" Real-time eBay UK sold prices, price trends, and mispricing detection for 100+ product categories.

2. **UKGraph** — UK labor market intelligence. "Is there room for me?" / "Should I switch careers?" ONS job advert data, career crowding scores, trade demand-to-worker ratios, and business formation/closure tracking by region.

3. **PowPowPow** — Compute economics. "Should I mine this?" / "Where should my GPUs go?" Live profitability calculations across 17+ proof-of-work networks, hardware comparisons, and hashrate migration tracking.

## How users will use it

### Example conversations:

**User (checking eBay listing):**
> "I found a Technics SL-1210 for £180 at a car boot sale. Should I buy it?"

**Muse calls DataGarden:**
```
breadup_valuation(query="technics sl-1210")
→ median sold: £245, liquidity: high, price trend: stable
```

**Muse responds:**
> "The SL-1210 sells for £245 median on eBay UK. At £180 that's a 27% margin. Condition matters though — good ones sell at £280, fair at £210. Worth it if it works."

---

**User (career decision):**
> "Should I retrain into cybersecurity?"

**Muse calls DataGarden:**
```
ukgraph_career_crowding(occupation="cybersecurity")
→ crowding score: 7.2/10, demand growth: +18%, entrant growth: +31%
```

**Muse responds:**
> "Cybersecurity demand is up 18% but entrants grew 31% — it's getting crowded. Data engineering has a better ratio right now (demand +24%, entrants +11%). If you're set on security, cloud securityspecialist has more room than generic SOC analyst."

---

**User (mining decision):**
> "I have 4x RTX 4090s. Should I mine Qubic or rent them out for AI inference?"

**Muse calls DataGarden:**
```
pow_mining_profitability(network="QUBIC", hardware="RTX_4090")
pow_best_mining(hardware="RTX_4090")
```

**Muse responds:**
> "Qubic mining with 4x 4090s yields about $X/day after electricity. AI inference rental on Vast.ai currently pays $Y/day for equivalent hardware. The gap is Z% — inference is more profitable right now, but Qubic has been trending up this week."

## Connector type
REST API — DataGarden exposes an MCP server (Model Context Protocol) that Muse can call as a connector.

## API surface
- `breadup_valuation(query)` — item price lookup
- `breadup_mispricing(category)` — find deals
- `breadup_price_history(query)` — price trends
- `ukgraph_career_crowding(occupation)` — career crowding analysis
- `ukgraph_trade_demand(trade)` — trade demand ratios
- `ukgraph_business_gap(postcode)` — local business opportunities
- `pow_network_status(network)` — network health
- `pow_mining_profitability(network, hardware)` — profitability calc
- `pow_best_mining(hardware)` — best mining option
- `pow_compare_networks(networks)` — cross-network comparison
- `garden_health()` — system status

## Data freshness
- PowPowPow: updated hourly (live API data)
- UKGraph (ONS): updated daily
- Breadup (eBay): updated daily
- Companies House: real-time streaming

## Cost to users
Free. DataGarden is a free data service funded by content (YouTube Shorts) and premium API access.

## Why this matters for Muse
DataGarden gives Muse answers that require **persistent real-world measurement** — not just what an LLM was trained on. When a user asks "should I buy this?" or "is this job worth taking?", Muse can give answers backed by actual market data, not generic advice.

The moat: historical data series that compound over time. A competitor can check today's prices. They can't see 6 months of depreciation curves or verified prediction accuracy.

## Contact
[Your contact info]

## Technical notes
- MCP server: `python mcp_server.py --serve` (stdio transport)
- Also works as CLI: `python mcp_server.py <tool> '<json_args>'`
- Data stored as JSONL files in forests/ directory
- All collectors are free (no API keys required for core functionality)
