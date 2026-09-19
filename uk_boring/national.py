"""National primitives — workflows identical across all UK councils.

These are the 80% that doesn't change. Every Place inherits them.
Local overrides only apply to the council-specific parts.
"""

from dataclasses import dataclass, field

@dataclass
class NationalWorkflow:
    """A workflow that works identically everywhere in the UK."""
    workflow_id: str
    name: str
    description: str
    category: str           # address_change, licence, tax, voting
    url: str                # official GOV.UK URL
    requires: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    receipt_pattern: dict = field(default_factory=dict)


# ============================================================
# ADDRESS CHANGE — national layer
# ============================================================

DVLA_ADDRESS_CHANGE = NationalWorkflow(
    workflow_id="national.dvla.address_change",
    name="Update driving licence address",
    description="Change address on DVLA driving licence",
    category="address_change",
    url="https://www.gov.uk/change-address-driving-licence",
    requires=["full_name", "new_address", "current_licence"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/change-address-driving-licence", "action_class": "PREPARE"},
        {"step": "authenticate", "action_class": "USER_HANDOFF", "note": "User must sign in with GOV.UK Verify"},
        {"step": "fill_form", "action_class": "APPROVAL_REQUIRED", "fields": ["name", "new_address", "licence_number"]},
        {"step": "submit", "action_class": "APPROVAL_REQUIRED", "note": "User approves submission"},
        {"step": "capture_confirmation", "action_class": "AUTO", "note": "Capture reference number"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "reference", "pattern": "DL-\\d{4}-\\d{5}"},
            {"name": "status", "contains": "application"},
        ],
    },
)

VEHICLE_TAX_ADDRESS = NationalWorkflow(
    workflow_id="national.vehicle_tax.address_change",
    name="Update vehicle tax address",
    description="Update address on DVLA vehicle tax records",
    category="address_change",
    url="https://www.gov.uk/vehicle-tax",
    requires=["vehicle_registration", "new_address", "reference_number"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/vehicle-tax", "action_class": "PREPARE"},
        {"step": "enter_details", "action_class": "APPROVAL_REQUIRED", "fields": ["registration", "reference"]},
        {"step": "update_address", "action_class": "APPROVAL_REQUIRED"},
        {"step": "capture_confirmation", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "vehicle_registration", "exists": True},
            {"name": "tax_status", "one_of": ["taxed", "SORN"]},
        ],
    },
)

ELECTORAL_REGISTER = NationalWorkflow(
    workflow_id="national.electoral.register",
    name="Register to vote",
    description="Register to vote at your address",
    category="voting",
    url="https://www.gov.uk/register-to-vote",
    requires=["full_name", "address", "national_insurance_number"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/register-to-vote", "action_class": "PREPARE"},
        {"step": "fill_form", "action_class": "USER_HANDOFF", "note": "User completes form"},
        {"step": "capture_confirmation", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "reference", "exists": True},
            {"name": "status", "contains": "registered"},
        ],
    },
)

HMRC_ADDRESS_CHANGE = NationalWorkflow(
    workflow_id="national.hmrc.address_change",
    name="Update HMRC address",
    description="Notify HMRC of new address for tax purposes",
    category="address_change",
    url="https://www.gov.uk/log-in-register-hmrc-online-services",
    requires=["full_name", "new_address"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/log-in-register-hmrc-online-services", "action_class": "PREPARE"},
        {"step": "authenticate", "action_class": "USER_HANDOFF", "note": "User signs in to HMRC"},
        {"step": "update_address", "action_class": "USER_HANDOFF", "note": "User updates in portal"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "status", "contains": "updated"},
        ],
    },
)


# ============================================================
# VEHICLE CHECKS — national layer
# ============================================================

MOT_CHECK = NationalWorkflow(
    workflow_id="national.mot.check",
    name="Check MOT history",
    description="Check MOT history for a vehicle",
    category="vehicle",
    url="https://www.gov.uk/check-mot-history",
    requires=["vehicle_registration"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/check-mot-history", "action_class": "PREPARE"},
        {"step": "enter_registration", "action_class": "AUTO", "fields": ["registration"]},
        {"step": "capture_results", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "results_page",
        "fields": [
            {"name": "registration", "exists": True},
            {"name": "make", "exists": True},
            {"name": "mot_expiry", "pattern": "\\d{2}/\\d{2}/\\d{4}"},
        ],
    },
)

VEHICLE_TAX_CHECK = NationalWorkflow(
    workflow_id="national.vehicle_tax.check",
    name="Check vehicle tax status",
    description="Check if vehicle tax is current",
    category="vehicle",
    url="https://www.gov.uk/check-vehicle-tax",
    requires=["vehicle_registration"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/check-vehicle-tax", "action_class": "PREPARE"},
        {"step": "enter_registration", "action_class": "AUTO", "fields": ["registration"]},
        {"step": "capture_results", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "results_page",
        "fields": [
            {"name": "registration", "exists": True},
            {"name": "tax_status", "one_of": ["taxed", "SORN", "expired", "not taxed"]},
        ],
    },
)


# ============================================================
# COMPANY CHECKS — national layer
# ============================================================

COMPANY_CHECK = NationalWorkflow(
    workflow_id="national.companies_house.check",
    name="Check company details",
    description="Look up company on Companies House",
    category="business",
    url="https://find-and-update.company-information.service.gov.uk/",
    requires=["company_number"],
    steps=[
        {"step": "api_lookup", "action_class": "AUTO", "mode": "api"},
        {"step": "capture_results", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "api_response",
        "fields": [
            {"name": "company_number", "exists": True},
            {"name": "company_name", "exists": True},
            {"name": "status", "one_of": ["active", "dissolved", "liquidation"]},
        ],
    },
)


# ============================================================
# COUNCIL TAX CHECK — national interface, local data
# ============================================================

COUNCIL_TAX_CHECK = NationalWorkflow(
    workflow_id="national.council_tax.check",
    name="Check council tax band",
    description="Look up council tax band for an address",
    category="council_tax",
    url="https://www.gov.uk/council-tax-bands",
    requires=["postcode"],
    steps=[
        {"step": "navigate", "url": "https://www.gov.uk/council-tax-bands", "action_class": "PREPARE"},
        {"step": "enter_postcode", "action_class": "AUTO", "fields": ["postcode"]},
        {"step": "capture_results", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "results_page",
        "fields": [
            {"name": "band", "one_of": ["A","B","C","D","E","F","G","H"]},
            {"name": "council", "exists": True},
        ],
    },
)


# ============================================================
# COUNCIL TAX MOVE HOME — national template
# ============================================================

COUNCIL_TAX_MOVE_HOME = NationalWorkflow(
    workflow_id="national.council_tax.move_home",
    name="Notify council of move",
    description="Notify council tax department of change of address",
    category="address_change",
    url="",  # local councils provide their own URL
    requires=["council_tax_reference", "new_address", "move_date"],
    steps=[
        {"step": "navigate", "url": "", "action_class": "PREPARE", "note": "Local council URL required"},
        {"step": "enter_details", "action_class": "APPROVAL_REQUIRED", "fields": ["reference", "new_address", "move_date"]},
        {"step": "capture_confirmation", "action_class": "AUTO"},
    ],
    receipt_pattern={
        "type": "confirmation_page",
        "fields": [
            {"name": "reference", "exists": True},
            {"name": "status", "contains": "updated"},
        ],
    },
)


# ============================================================
# REGISTRY
# ============================================================

NATIONAL_WORKFLOWS = {
    "national.dvla.address_change": DVLA_ADDRESS_CHANGE,
    "national.vehicle_tax.address_change": VEHICLE_TAX_ADDRESS,
    "national.electoral.register": ELECTORAL_REGISTER,
    "national.hmrc.address_change": HMRC_ADDRESS_CHANGE,
    "national.mot.check": MOT_CHECK,
    "national.vehicle_tax.check": VEHICLE_TAX_CHECK,
    "national.companies_house.check": COMPANY_CHECK,
    "national.council_tax.check": COUNCIL_TAX_CHECK,
    "national.council_tax.move_home": COUNCIL_TAX_MOVE_HOME,
}

def get_national_workflow(workflow_id: str) -> NationalWorkflow:
    return NATIONAL_WORKFLOWS.get(workflow_id)

def list_national_workflows(category: str = None) -> list:
    if category:
        return [w for w in NATIONAL_WORKFLOWS.values() if w.category == category]
    return list(NATIONAL_WORKFLOWS.values())
