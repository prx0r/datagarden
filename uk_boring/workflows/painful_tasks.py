"""UK Painful Tasks — Workflow definitions for the most annoying UK bureaucratic tasks.

Based on real complaint data from:
- Parliament reports on DVLA backlogs
- Council Tax statistics
- Citizens Advice data
- Council parking data
- Energy Ombudsman reports
"""

from dataclasses import dataclass, field


@dataclass
class PainfulTask:
    """Definition of a UK bureaucratic workflow."""
    workflow_id: str
    name: str
    volume: str
    source: str
    url: str
    cost: str
    timeline: str
    category: str
    steps: list = field(default_factory=list)
    requires: list = field(default_factory=list)
    receipt_pattern: dict = field(default_factory=dict)
    failure_modes: list = field(default_factory=list)


# ============================================================================
# Workflow Definitions
# ============================================================================

DVLA_LICENCE_RENEWAL = PainfulTask(
    workflow_id="dvla.renew_licence",
    name="DVLA Licence Renewal",
    volume="3,000,000+ customers affected",
    source="Parliament report on DVLA backlogs",
    url="https://www.gov.uk/renew-driving-licence",
    cost="£14 online / £21.50 Post Office / £17 post",
    timeline="1 week online, 3 weeks post",
    category="licence",
    requires=["full_name", "address", "licence_number"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/renew-driving-licence", "action_class": "PREPARE"},
        {"step": "authenticate", "action_class": "USER_HANDOFF", "note": "User must sign in with GOV.UK Verify"},
        {"step": "fill_form", "action_class": "APPROVAL_REQUIRED", "fields": ["name", "address", "licence_number"]},
        {"step": "submit", "action_class": "APPROVAL_REQUIRED", "note": "User approves submission"},
        {"step": "capture_confirmation", "action_class": "AUTO", "note": "Capture reference number"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "reference", "pattern": "DL-\\d{4}-\\d{5}"},
            {"name": "status", "contains": "application received"},
            {"name": "timeline", "contains": "within 3 weeks"},
        ],
    },
    failure_modes=[
        {"name": "name_changed", "description": "must apply by post"},
        {"name": "signature_changed", "description": "must apply by post"},
        {"name": "medical", "description": "additional checks required"},
    ],
)

COUNCIL_TAX_BAND_CHALLENGE = PainfulTask(
    workflow_id="council_tax.band_challenge",
    name="Council Tax Band Challenge",
    volume="millions affected",
    source="Council Tax statistics",
    url="https://www.gov.uk/council-tax-bands",
    cost="Free",
    timeline="2 months for decision",
    category="council_tax",
    requires=["postcode", "address", "current_band"],
    steps=[
        {"step": "check_band", "action_class": "AUTO", "note": "Look up current band via VOA"},
        {"step": "gather_evidence", "action_class": "USER_HANDOFF", "note": "Find comparable properties in same area"},
        {"step": "submit_challenge", "url": "https://www.gov.uk/council-tax-bands", "action_class": "APPROVAL_REQUIRED"},
        {"step": "await_decision", "action_class": "AUTO", "note": "Up to 2 months for VOA decision"},
        {"step": "receive_outcome", "action_class": "AUTO", "note": "Band changed or maintained"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "reference", "exists": True},
            {"name": "status", "one_of": ["challenge received", "decision made"]},
            {"name": "band", "one_of": ["A", "B", "C", "D", "E", "F", "G", "H"]},
        ],
    },
    failure_modes=[
        {"name": "insufficient_evidence", "description": "need comparable properties"},
        {"name": "wrong_property", "description": "address mismatch"},
        {"name": "already_challenged", "description": "within 6 months"},
    ],
)

PARKING_FINE_APPEAL = PainfulTask(
    workflow_id="parking.pcn_appeal",
    name="Parking Fine Appeal (PCN)",
    volume="millions issued",
    source="Council parking data",
    url="varies by council",
    cost="Free to appeal, £70-130 if not appealed",
    timeline="28 days to appeal",
    category="parking",
    requires=["pcn_number", "council", "notice_date"],
    steps=[
        {"step": "receive_pcn", "action_class": "AUTO", "note": "Extract PCN details from notice"},
        {"step": "check_validity", "action_class": "AUTO", "note": "Was PCN correctly issued?"},
        {"step": "gather_evidence", "action_class": "USER_HANDOFF", "note": "Photos, signage, circumstances"},
        {"step": "submit_appeal", "action_class": "APPROVAL_REQUIRED", "note": "Council online form or letter"},
        {"step": "await_decision", "action_class": "AUTO", "note": "2-8 weeks for response"},
        {"step": "if_rejected", "action_class": "USER_HANDOFF", "note": "Tribunal appeal within 28 days"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "pcn_number", "exists": True},
            {"name": "status", "one_of": ["appeal received", "decision"]},
            {"name": "outcome", "one_of": ["upheld", "overturned", "reduced"]},
        ],
    },
    failure_modes=[
        {"name": "missed_deadline", "description": "28-day limit"},
        {"name": "insufficient_evidence", "description": "no photos"},
        {"name": "wrong_council", "description": "wrong authority"},
    ],
)

USED_CAR_COMPLAINT = PainfulTask(
    workflow_id="used_car.complaint",
    name="Used Car Complaint",
    volume="52,304/year (17.8% of all consumer complaints)",
    source="Citizens Advice",
    url="varies by seller",
    cost="Free to complain, possible small claims",
    timeline="2-8 weeks",
    category="consumer",
    requires=["seller_name", "purchase_date", "description_of_fault"],
    steps=[
        {"step": "document_fault", "action_class": "USER_HANDOFF", "note": "Photos, receipts, correspondence"},
        {"step": "contact_seller", "action_class": "APPROVAL_REQUIRED", "note": "Written complaint with deadline"},
        {"step": "await_response", "action_class": "AUTO", "note": "14 days for seller response"},
        {"step": "escalate", "action_class": "USER_HANDOFF", "note": "Trading Standards or ombudsman"},
        {"step": "if_unresolved", "action_class": "USER_HANDOFF", "note": "Small claims court"},
    ],
    receipt_pattern={
        "type": "complaint_reference",
        "fields": [
            {"name": "reference", "exists": True},
            {"name": "status", "one_of": ["complaint sent", "response received", "resolved"]},
            {"name": "outcome", "one_of": ["repair", "refund", "replacement", "partial"]},
        ],
    },
    failure_modes=[
        {"name": "no_receipt", "description": "missing proof of purchase"},
        {"name": "outside_warranty", "description": "30-day right to reject expired"},
        {"name": "seller_unresponsive", "description": "need to escalate"},
    ],
)

ENERGY_BILL_DISPUTE = PainfulTask(
    workflow_id="energy.bill_dispute",
    name="Energy Bill Dispute",
    volume="24,000 referrals to EHU/year",
    source="Citizens Advice",
    url="varies by supplier",
    cost="Free to complain",
    timeline="5-25 weeks",
    category="energy",
    requires=["supplier_name", "account_number", "disputed_amount"],
    steps=[
        {"step": "gather_evidence", "action_class": "USER_HANDOFF", "note": "Bills, meter readings, contract"},
        {"step": "contact_supplier", "action_class": "APPROVAL_REQUIRED", "note": "Formal complaint"},
        {"step": "await_response", "action_class": "AUTO", "note": "8 weeks for supplier response"},
        {"step": "escalate", "action_class": "USER_HANDOFF", "note": "Energy Ombudsman"},
        {"step": "if_unresolved", "action_class": "USER_HANDOFF", "note": "Citizens Advice EHU"},
    ],
    receipt_pattern={
        "type": "complaint_reference",
        "fields": [
            {"name": "reference", "exists": True},
            {"name": "status", "one_of": ["complaint sent", "response", "resolved"]},
            {"name": "outcome", "one_of": ["correction", "compensation", "deadlock letter"]},
        ],
    },
    failure_modes=[
        {"name": "no_meter_readings", "description": "need actual readings"},
        {"name": "outside_supplier", "description": "wrong company"},
        {"name": "old_bills", "description": "need recent evidence"},
    ],
)


# ============================================================================
# Registry
# ============================================================================

PAINFUL_TASKS = {
    "dvla.renew_licence": DVLA_LICENCE_RENEWAL,
    "council_tax.band_challenge": COUNCIL_TAX_BAND_CHALLENGE,
    "parking.pcn_appeal": PARKING_FINE_APPEAL,
    "used_car.complaint": USED_CAR_COMPLAINT,
    "energy.bill_dispute": ENERGY_BILL_DISPUTE,
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_painful_task(workflow_id: str) -> PainfulTask:
    """Get a painful task workflow by ID."""
    return PAINFUL_TASKS.get(workflow_id)


def list_painful_tasks(category: str = None) -> list:
    """List all painful task workflows, optionally filtered by category."""
    if category:
        return [t for t in PAINFUL_TASKS.values() if t.category == category]
    return list(PAINFUL_TASKS.values())
