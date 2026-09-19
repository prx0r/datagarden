"""UKOpportunity Garden Contract.

Mission: Continuously measure real economic opportunities and match them to capabilities people already control.

Routes it materially improves:
- earn() returns work, gigs, contracts, leads, flips
- find() returns local suppliers and services
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
    """Garden Contract for UKOpportunity.

    Hard rule: No Garden Contract without at least one Route it materially improves.
    """

    name: str = "UKOpportunity"

    user_goal_enabled: tuple[str, ...] = (
        "earn -- What can I do to make money?",
        "find -- Find someone/something capable of satisfying this requirement.",
        "watch -- Tell me when something useful changes.",
    )

    raw_sources: tuple[str, ...] = (
        "job_board_listings",
        "gig_marketplace_listings",
        "public_procurement_tenders",
        "planning_applications",
        "council_contract_awards",
        "supplier_directory_entries",
        "local_business_registry",
        "capability_vacancy_signals",
        "equipment_repair_listings",
        "marketplace_demand_signals",
        "grant_programme_announcements",
        "event_staffing_notices",
    )

    unique_transformation: str = (
        "Cross-join current opportunity signals with historical capability scarcity, "
        "realised outcome rates, and local demand patterns to produce ranked, "
        "evidence-backed Routes that match economically actionable opportunities "
        "to capability envelopes a personal agent can act on. "
        "Not search results -- actionable economic routes with provenance, "
        "expected value, and verified outcome calibration."
    )

    historical_state_retained: str = (
        "Listing appearance/disappearance over time; time-to-fill per capability "
        "in a locale; historical conversion rates (shown -> applied -> accepted "
        "-> completed -> paid); observed wage/price trends; supplier population "
        "density through time; planning application outcomes; contract award "
        "patterns; demand seasonality; local scarcity score history."
    )

    snapshot_or_event_frequency: str = (
        "Daily snapshots of high-volume sources (job boards, marketplace listings). "
        "Event-driven ingestion for tenders, planning applications, and grant "
        "announcements as they appear. Weekly re-aggregation of scarcity scores "
        "and conversion baselines."
    )

    outputs: tuple[str, ...] = (
        "Route(route_type in {JOB, GIG, CONTRACT, LEAD, FLIP, GRANT, SERVICE, TRAINING})",
        "CapabilityScarcity (place x capability x time)",
        "OpportunityConversionHistory",
        "LocalDemandSignal",
        "SupplierPopulationDensity",
    )

    proof_loop: str = (
        "Route offered -> user/agent acts (application, quote, purchase) -> "
        "external evidence collected (submission acknowledgement, booking "
        "confirmation, payment received) -> Receipt settles TRUE/FALSE/UNKNOWN "
        "independently of agent assertion -> outcome updates conversion "
        "calibration for this capability-in-place combination -> future Routes "
        "re-weighted by verified historical success rate."
    )

    failure_modes: tuple[str, ...] = (
        "SOURCE_DOWN -- primary listing source unreachable or blocked",
        "SOURCE_SCHEMA_CHANGED -- listing format changed, parser broken",
        "STALE_DATA -- listings no longer reflect real availability",
        "ENTITY_AMBIGUOUS -- cannot reliably resolve employer/organisation identity",
        "SEMANTIC_UNCERTAIN -- Jev classification of capability requirements uncertain",
        "ROUTE_EXPIRED -- opportunity window closed before agent acted",
        "CONVERSION_CONTAMINATED -- self-reinforcing AI-generated routes without "
        "grounding in real external listings",
        "SCARCITY_PROXY_UNRELIABLE -- proxy supply/demand signals diverge from "
        "actual local economic reality",
    )

    irrecoverable_asset: str = (
        "Historical capability-in-place scarcity time series and verified outcome "
        "conversion rates. Once a listing disappears or an opportunity window "
        "closes, only our retained temporal record preserves the ground truth of "
        "what was available, who filled it, how fast, and at what price. This "
        "historical relationship between signal -> recommendation -> action -> "
        "verified outcome is the deepest moat and cannot be reconstructed from "
        "tomorrow's live web."
    )

    expected_maintenance: str = (
        "Parser maintenance as job boards and marketplace UIs change (estimated "
        "2-4 sources requiring quarterly review). Jev DecisionSpec calibration "
        "for capability inference as new occupation types emerge. Source health "
        "monitoring with automatic staleness alerts. Quarterly review of "
        "conversion baseline assumptions against new receipt evidence."
    )

    source_licences: tuple[str, ...] = (
        "Government open data (OGL 3.0) for planning applications and "
        "council contracts where applicable.",
        "Job board terms of service -- scraping robots.txt compliance, "
        "rate limiting, no personal data retention.",
        "Public procurement portals -- Open Contracting Data Standard "
        "where available.",
        "Marketplace APIs -- terms vary per platform, usage within "
        "permitted access patterns.",
    )

    acceptance_tests: tuple[str, ...] = (
        "TEST_OPPORTUNITY_ROUTE_EXISTS: earn() returns at least one Route of "
        "type JOB, GIG, or CONTRACT from a real current listing for a valid "
        "CapabilityEnvelope in Oldham.",
        "TEST_ROUTE_HAS_EVIDENCE: Every returned Route includes at minimum "
        "source_url_or_ref, observed_at, raw_artifact_hash, and licence in "
        "its evidence chain.",
        "TEST_ROUTE_HAS_FRESHNESS: Every Route exposes last_observed and "
        "stale flag; stale Routes are either excluded or carry explicit "
        "uncertainty annotation.",
        "TEST_ROUTE_HAS_ACTION: Every Route includes an execution block "
        "with type and target sufficient for a personal agent to initiate action.",
        "TEST_ROUTE_FAMILY_DIVERSITY: For the benchmark query 'I need £300 "
        "this weekend in Oldham', earn() returns routes from at least two "
        "distinct route_type families (e.g. JOB + FLIP, or GIG + CONTRACT).",
        "TEST_SCARCITY_SIGNAL: CapabilityScarcity for a known scarce "
        "capability in Oldham returns a scarcity_score above baseline and "
        "includes evidence from at least two independent source observations.",
        "TEST_PROOF_LOOP: A Route that was acted upon (submission acknowledged) "
        "has a Receipt with result TRUE or FALSE settled from external evidence "
        "within 14 days of action, not from the agent's own assertion.",
        "TEST_CONVERSION_CALIBRATION: After 50+ verified outcomes for a "
        "capability-place pair, the predicted success probability is within "
        "15 percentage points of the observed conversion rate.",
        "TEST_HISTORICAL_IRRECOVERABILITY: For any capability-place pair with "
        "30+ days of history, a historical valuation query returns data that "
        "differs from what the current live web would show (e.g. a listing "
        "that no longer exists).",
    )
