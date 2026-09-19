"""UKProducts Garden Contract.

Mission: Model what physical things are actually worth, how liquid they are, and what economic actions they enable.

Routes it materially improves:
- value() returns accurate valuations
- flip routes with margin estimates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class Frequency(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVENT = "event"


@dataclass(frozen=True)
class GardenContract:
    """Garden Contract for UKProducts.

    Hard rule: No Garden Contract without at least one Route it materially improves.
    """

    name: str = "UKProducts"

    user_goal_enabled: tuple[str, ...] = (
        "value -- What is this actually worth?",
        "earn -- Repair/flip routes with margin estimates and liquidity predictions.",
        "watch -- Tell me when something useful changes (price threshold, new listing).",
    )

    raw_sources: tuple[str, ...] = (
        "marketplace_listings_active",
        "marketplace_listings_expired",
        "completed_sale_records",
        "auction_house_results",
        "repair_cost_databases",
        "product_specification_catalogues",
        "condition_grading_references",
        "regional_price_indices",
        "secondhand_dealer_inventories",
        "enthusiast_forum_price_threads",
    )

    unique_transformation: str = (
        "Resolve messy product listings to canonical product/variant/condition "
        "identity, join with historical sold prices and listing duration, "
        "compute market value, liquidity (days-to-sale), spread (buy-sell gap), "
        "trend, repair cost estimate, and flip margin. "
        "Not a price lookup -- a temporal economic model of what things are "
        "worth, how fast they move, and what profit is realistic for a given "
        "person with given capabilities."
    )

    historical_state_retained: str = (
        "Listing price and availability through time for every observed "
        "product/variant/condition tuple. Completed sale prices with dates. "
        "Listing duration (first_seen to sold_or_expired). Price trend "
        "direction and magnitude. Condition distribution over time. "
        "Marketplace venue differences. Regional price variation. "
        "Repair cost history by fault type."
    )

    snapshot_or_event_frequency: str = (
        "Daily snapshots of active marketplace listings across tracked "
        "categories. Event-driven ingestion when completed sales are observed. "
        "Weekly re-computation of trend, liquidity, and margin estimates. "
        "Monthly recalibration of repair cost models against new evidence."
    )

    outputs: tuple[str, ...] = (
        "Route(route_type in {FLIP, SALE})",
        "ProductValuation(product, variant, condition) -> market_value, confidence",
        "ProductLiquidity(product, variant) -> days_to_sale, sale_probability",
        "ProductSpread(product, variant, condition) -> buy_price, expected_sell_price, margin",
        "ProductTrend(product, variant) -> direction, magnitude, evidence",
        "RepairSpread(asset, fault) -> listing_price, parts_cost, repaired_value, net_margin",
    )

    proof_loop: str = (
        "Route offered (buy item -> repair -> sell) -> agent acts (purchases, "
        "repairs, lists) -> external evidence observed (sale completed, price "
        "realised) -> Receipt settles TRUE/FALSE/UNKNOWN -> outcome updates "
        "liquidity model, margin accuracy, and trend calibration for this "
        "product family -> future Routes re-weighted by verified realised "
        "margins."
    )

    failure_modes: tuple[str, ...] = (
        "SOURCE_DOWN -- marketplace unreachable or blocked",
        "SOURCE_SCHEMA_CHANGED -- listing format changed, parser broken",
        "STALE_DATA -- historical prices no longer reflect current market",
        "ENTITY_AMBIGUOUS -- cannot resolve exact product/variant/pressing "
        "from listing description",
        "CONDITION_MISCLASSIFIED -- seller-described condition does not match "
        "actual condition, contaminating price series",
        "ILLIQUID_CATEGORY -- insufficient transaction history to produce "
        "meaningful liquidity or margin estimates",
        "VENUE_BLINDNESS -- prices differ materially between marketplace "
        "venues but data only covers one",
        "REPAIR_COST_DRIFT -- parts or labour costs shift faster than model "
        "updates, eroding margin accuracy",
    )

    irrecoverable_asset: str = (
        "Historical price time series with identity resolution to exact "
        "product/variant/condition, including disappeared listings and "
        "completed sales. Once a listing expires or is removed, the web "
        "cannot recover the exact price, condition description, and listing "
        "duration. Ten years of condition-normalised pressing-level vinyl "
        "prices, including disappeared listings, cannot be reconstructed. "
        "This temporal depth is the deepest moat."
    )

    expected_maintenance: str = (
        "Parser maintenance as marketplace UIs and listing formats change "
        "(estimated 3-6 marketplaces requiring quarterly review). Product "
        "identity resolution model updates as new product families are "
        "added. Repair cost model recalibration against new sale evidence. "
        "Source health monitoring with staleness alerts. Quarterly liquidity "
        "model validation against actual days-to-sale in recent receipts."
    )

    source_licences: tuple[str, ...] = (
        "Marketplace terms of service -- scraping within robots.txt and "
        "rate limits, no personal data retention.",
        "Completed sale data where publicly visible -- fair use for "
        "aggregation and transformation.",
        "Enthusiast forum data -- public posts, attribution preserved.",
        "Product specification catalogues -- manufacturer-published "
        "specifications, OGL where government-sourced.",
    )

    acceptance_tests: tuple[str, ...] = (
        "TEST_VALUATION_EXISTS: value() returns a ProductValuation with "
        "market_value and confidence for a canonical product/variant/condition "
        "tuple observed in at least 10 historical data points.",
        "TEST_VALUATION_ACCURACY: For products with 20+ completed sales in "
        "the last 90 days, the predicted market_value is within 20% of the "
        "median realised sale price.",
        "TEST_LIQUIDITY_PREDICTION: For products with 15+ completed sales, "
        "predicted days_to_sale is within 5 days of the observed median.",
        "TEST_FLIP_ROUTE_HAS_MARGIN: A FLIP route includes listing_price, "
        "expected_parts_cost, expected_repaired_value, and expected_net_margin "
        "with explicit uncertainty for each component.",
        "TEST_ROUTE_HAS_EVIDENCE: Every Route includes at minimum "
        "source_url_or_ref, observed_at, raw_artifact_hash, and licence.",
        "TEST_HISTORICAL_IRRECOVERABILITY: For any product family with 60+ "
        "days of history, a historical valuation query returns price data "
        "that includes at least one listing no longer visible on the live "
        "marketplace.",
        "TEST_REPAIR_SPREAD: A RepairSpread for a known repairable item "
        "returns listing_price, parts_cost, repaired_value, and net_margin, "
        "with parts_cost marked UNKNOWN when evidence is insufficient.",
        "TEST_CONDITION_NORMALISATION: Two listings describing the same "
        "product in different seller terminology resolve to the same "
        "canonical condition grade.",
        "TEST_TREND_DIRECTION: For a product family with 30+ days of "
        "continuous observation, trend direction (up/down/stable) agrees "
        "with a simple linear regression on the price series at p < 0.10.",
    )
