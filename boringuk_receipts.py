"""Receipt verification for UK Boring workflows.

Defines expected receipt patterns for government form submissions
and verifies Muse's captured confirmations against them.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class VerificationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass
class FieldPattern:
    """Expected pattern for a single field in a confirmation."""
    field_name: str
    pattern: Optional[str] = None      # regex pattern
    contains: Optional[str] = None     # must contain this string
    one_of: Optional[list] = None      # must be one of these values
    matches: Optional[str] = None      # must match another field's value
    exists: bool = False               # must be present
    type: str = "string"               # string, array, number


@dataclass
class FailurePattern:
    """Pattern that indicates a known failure mode."""
    contains: str
    action: str         # what to do: switch, inform_user, user_handoff, etc.
    description: str = ""


@dataclass
class ReceiptPattern:
    """Expected receipt for a workflow step."""
    step_id: str
    step_name: str
    method: str            # online, api, phone, post
    url: str               # where this happens
    receipt_type: str      # confirmation_page, results_page, api_response, etc.
    
    # What success looks like
    fields: list = field(default_factory=list)        # list of FieldPattern
    failure_patterns: list = field(default_factory=list)  # list of FailurePattern
    
    # Verification settings
    confidence: float = 0.9
    evidence_type: str = "confirmation_page"  # screenshot, api_response, email, etc.
    notes: str = ""
    
    # Metadata
    version: int = 1
    last_verified: str = ""
    success_rate: float = 0.0


@dataclass
class VerificationOutcome:
    """Result of verifying a captured confirmation."""
    step_id: str
    result: VerificationResult
    confidence: float
    matched_fields: list = field(default_factory=list)
    failed_fields: list = field(default_factory=list)
    failure_action: Optional[str] = None
    evidence: list = field(default_factory=list)
    receipt_data: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)


def verify_receipt(pattern: ReceiptPattern, captured: dict, known_fields: dict = None) -> VerificationOutcome:
    """Verify a captured confirmation against an expected receipt pattern.
    
    Args:
        pattern: The expected receipt pattern
        captured: What Muse captured (field_name -> value)
        known_fields: User/system context (name, address, vehicle, etc.)
    
    Returns:
        VerificationOutcome with PASS/FAIL/UNKNOWN
    """
    known_fields = known_fields or {}
    matched = []
    failed = []
    receipt_data = {}
    notes = []
    
    # Check failure patterns first
    captured_text = json.dumps(captured, default=str).lower()
    for fp in pattern.failure_patterns:
        if fp.contains.lower() in captured_text:
            return VerificationOutcome(
                step_id=pattern.step_id,
                result=VerificationResult.FAIL,
                confidence=0.95,
                failure_action=fp.action,
                evidence=[f"Failure pattern matched: {fp.contains}"],
                notes=[fp.description or fp.action],
            )
    
    # Check each expected field
    for field_pattern in pattern.fields:
        value = captured.get(field_pattern.field_name)
        
        if field_pattern.exists and value is None:
            failed.append(f"{field_pattern.field_name}: missing")
            continue
        
        if value is None:
            notes.append(f"{field_pattern.field_name}: not captured, skipping")
            continue
        
        field_ok = True
        
        # Check pattern match
        if field_pattern.pattern:
            if not re.search(field_pattern.pattern, str(value)):
                field_ok = False
                failed.append(f"{field_pattern.field_name}: '{value}' doesn't match /{field_pattern.pattern}/")
        
        # Check contains
        if field_pattern.contains:
            if field_pattern.contains.lower() not in str(value).lower():
                field_ok = False
                failed.append(f"{field_pattern.field_name}: '{value}' doesn't contain '{field_pattern.contains}'")
        
        # Check one_of
        if field_pattern.one_of:
            if str(value) not in field_pattern.one_of:
                field_ok = False
                failed.append(f"{field_pattern.field_name}: '{value}' not in {field_pattern.one_of}")
        
        # Check matches (compare to another field's value)
        if field_pattern.matches:
            other_value = captured.get(field_pattern.matches, known_fields.get(field_pattern.matches))
            if other_value and str(value) != str(other_value):
                field_ok = False
                failed.append(f"{field_pattern.field_name}: '{value}' doesn't match {field_pattern.matches}='{other_value}'")
        
        if field_ok:
            matched.append(field_pattern.field_name)
            receipt_data[field_pattern.field_name] = value
    
    # Calculate result
    total = len(pattern.fields)
    passed = len(matched)
    failed_count = len(failed)
    
    if failed_count == 0 and passed > 0:
        result = VerificationResult.PASS
        confidence = min(0.99, pattern.confidence + (passed / total) * 0.05)
    elif failed_count == 0 and passed == 0:
        result = VerificationResult.UNKNOWN
        confidence = 0.1
    else:
        result = VerificationResult.FAIL
        confidence = max(0.1, pattern.confidence - failed_count * 0.1)
    
    return VerificationOutcome(
        step_id=pattern.step_id,
        result=result,
        confidence=confidence,
        matched_fields=matched,
        failed_fields=failed,
        evidence=[f"Verified {passed}/{total} fields"],
        receipt_data=receipt_data,
        notes=notes,
    )


# ============================================================
# PREDEFINED RECEIPT PATTERNS
# ============================================================

RECEIPT_PATTERNS = {
    "dvla.renew.submit": ReceiptPattern(
        step_id="dvla.renew.submit",
        step_name="Renew driving licence",
        method="online",
        url="https://www.gov.uk/renew-driving-licence",
        receipt_type="confirmation_page",
        fields=[
            FieldPattern("reference", pattern=r"DL-\d{4}-\d{5}", exists=True),
            FieldPattern("status", contains="application"),
            FieldPattern("timeline", contains="week"),
        ],
        failure_patterns=[
            FailurePattern("cannot renew online", "switch_to_post_office", "Name or signature changed"),
            FailurePattern("name changed", "must_apply_by_post", "Name change requires post"),
            FailurePattern("signature changed", "must_apply_by_post", "Signature change requires post"),
        ],
        confidence=0.95,
    ),
    
    "electoral.register.submit": ReceiptPattern(
        step_id="electoral.register.submit",
        step_name="Register to vote",
        method="online",
        url="https://www.gov.uk/register-to-vote",
        receipt_type="confirmation_page",
        fields=[
            FieldPattern("reference", exists=True),
            FieldPattern("status", contains="registered"),
            FieldPattern("name", matches="user_full_name"),
        ],
        failure_patterns=[
            FailurePattern("not eligible", "inform_user", "Not eligible to register"),
            FailurePattern("already registered", "idempotent_success", "Already registered"),
        ],
        confidence=0.95,
    ),
    
    "dvsa.mot.lookup": ReceiptPattern(
        step_id="dvsa.mot.lookup",
        step_name="Check MOT history",
        method="online",
        url="https://www.gov.uk/check-mot-history",
        receipt_type="results_page",
        fields=[
            FieldPattern("registration", matches="vehicle_registration"),
            FieldPattern("make", exists=True),
            FieldPattern("model", exists=True),
            FieldPattern("mot_expiry", pattern=r"\d{2}/\d{2}/\d{4}"),
        ],
        failure_patterns=[
            FailurePattern("no record", "check_registration", "No MOT record found"),
            FailurePattern("not found", "verify_vehicle_details", "Vehicle not found"),
        ],
        confidence=0.99,
    ),
    
    "dvla.tax.submit": ReceiptPattern(
        step_id="dvla.tax.submit",
        step_name="Tax vehicle",
        method="online",
        url="https://www.gov.uk/vehicle-tax",
        receipt_type="confirmation_page",
        fields=[
            FieldPattern("vehicle_registration", matches="vehicle_registration"),
            FieldPattern("tax_status", one_of=["taxed", "SORN"]),
            FieldPattern("tax_due", pattern=r"\d{2}/\d{2}/\d{4}"),
        ],
        failure_patterns=[
            FailurePattern("no reference", "need_dvla_documents", "Need reference number"),
            FailurePattern("SORN", "confirm_sorn", "SORN registered"),
        ],
        confidence=0.95,
    ),
    
    "council_tax.lookup": ReceiptPattern(
        step_id="council_tax.lookup",
        step_name="Check council tax band",
        method="online",
        url="https://www.gov.uk/council-tax-bands",
        receipt_type="results_page",
        fields=[
            FieldPattern("band", one_of=["A","B","C","D","E","F","G","H"]),
            FieldPattern("council", exists=True),
            FieldPattern("annual_amount", pattern=r"£[\d,]+"),
        ],
        failure_patterns=[
            FailurePattern("scotland", "use_saa_gov_uk", "Scotland uses different system"),
        ],
        confidence=0.99,
    ),
    
    "companies_house.lookup": ReceiptPattern(
        step_id="companies_house.lookup",
        step_name="Check company",
        method="api",
        url="https://api.company-information.service.gov.uk/company/{number}",
        receipt_type="api_response",
        fields=[
            FieldPattern("company_number", matches="target_number"),
            FieldPattern("company_name", exists=True),
            FieldPattern("status", one_of=["active", "dissolved", "liquidation", "administration"]),
            FieldPattern("incorporation_date", pattern=r"\d{4}-\d{2}-\d{2}"),
        ],
        confidence=0.99,
    ),
    
    "council.report_missed_bin": ReceiptPattern(
        step_id="council.report_missed_bin",
        step_name="Report missed bin",
        method="online",
        url="{council_url}/report-missed-collection",
        receipt_type="confirmation_page",
        fields=[
            FieldPattern("reference", exists=True),
            FieldPattern("status", contains="reported"),
        ],
        confidence=0.85,
        notes="Council websites vary significantly",
    ),
}


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python receipt_verification.py <step_id>")
        print(f"Available steps: {list(RECEIPT_PATTERNS.keys())}")
        sys.exit(1)
    
    step_id = sys.argv[1]
    pattern = RECEIPT_PATTERNS.get(step_id)
    if not pattern:
        print(f"Unknown step: {step_id}")
        sys.exit(1)
    
    print(json.dumps({
        "step_id": pattern.step_id,
        "step_name": pattern.step_name,
        "url": pattern.url,
        "fields": [{"name": f.field_name, "pattern": f.pattern, "contains": f.contains, "one_of": f.one_of} for f in pattern.fields],
        "failure_patterns": [{"contains": fp.contains, "action": fp.action} for fp in pattern.failure_patterns],
        "confidence": pattern.confidence,
    }, indent=2))
