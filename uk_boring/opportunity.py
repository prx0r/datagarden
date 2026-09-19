"""Opportunity signals — what changed that creates value.

Planning approved → future demand
New business → economic activity
Contract published → procurement opportunity
Grant announced → funding available
"""

from datetime import datetime
from uk_boring.ontology import Signal, Opportunity


def process_planning_signal(application: dict, place_id: str) -> list[Signal]:
    """Turn a planning application into opportunity signals."""
    signals = []
    status = application.get("status", "").lower()

    if status in ("approved", "granted"):
        desc = application.get("description", "")
        ref = application.get("reference", "")
        signals.append(Signal(
            signal_id=f"plan_{ref}",
            place_id=place_id,
            signal_type="planning_approved",
            title=f"Development approved: {desc[:80]}",
            description=desc,
            source="planning_data",
            detected_at=datetime.now().isoformat(),
            strength=0.8,
        ))

    return signals


def process_business_signal(event: dict, place_id: str) -> list[Signal]:
    """Turn a new business registration into opportunity signals."""
    signals = []
    event_type = event.get("type", "").lower()

    if event_type == "new_registration":
        name = event.get("name", "")
        signals.append(Signal(
            signal_id=f"biz_{event.get('company_number', '')}",
            place_id=place_id,
            signal_type="new_business",
            title=f"New business: {name}",
            description=f"New business registered: {name}",
            source="companies_house",
            detected_at=datetime.now().isoformat(),
            strength=0.6,
        ))

    return signals


def process_contract_signal(contract: dict, place_id: str) -> list[Signal]:
    """Turn a published contract into opportunity signals."""
    signals = []
    title = contract.get("title", "")
    value = contract.get("value", 0)

    signals.append(Signal(
        signal_id=f"contract_{contract.get('id', '')}",
        place_id=place_id,
        signal_type="contract_published",
        title=f"Contract: {title}",
        description=f"New contract opportunity worth £{value:,.0f}",
        source="contracts_finder",
        detected_at=datetime.now().isoformat(),
        strength=0.9,
    ))

    return signals


def signals_to_opportunities(signals: list[Signal]) -> list[Opportunity]:
    """Convert raw signals into actionable opportunities."""
    opportunities = []
    for sig in signals:
        opp_type = _signal_to_opp_type(sig.signal_type)
        opportunities.append(Opportunity(
            opportunity_id=f"opp_{sig.signal_id}",
            place_id=sig.place_id,
            type=opp_type,
            title=sig.title,
            description=sig.description,
            source=sig.source,
            detected_at=sig.detected_at,
            evidence=[sig.description],
        ))
    return opportunities


def _signal_to_opp_type(signal_type: str) -> str:
    """Map signal type to opportunity type."""
    mapping = {
        "planning_approved": "demand_signal",
        "new_business": "business_gap",
        "contract_published": "contract",
        "grant_announced": "grant",
    }
    return mapping.get(signal_type, "demand_signal")
