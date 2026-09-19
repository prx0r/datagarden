# UK Boring — Receipt Patterns

## The insight

UK government forms are deterministic. We know:
- Every field in advance
- The submission URL
- What a success confirmation looks like
- What a failure looks like

So we can define the **expected receipt pattern** for every workflow step. Muse fills the form, captures the confirmation, QP verifies it matches, garden stores the verified outcome.

## How it works

```text
1. Define receipt pattern for each step
2. Muse executes the step (fills form, submits)
3. Muse captures: screenshot/HTML/reference number/email
4. QP verifies: does captured output match expected pattern?
5. Garden stores: verified outcome + evidence
```

## Receipt patterns for verified workflows

### 1. Renew driving licence (online)

```yaml
step: dvla.renew.submit
method: online
url: https://www.gov.uk/renew-driving-licence

expected_receipt:
  type: confirmation_page
  fields:
    - reference:
        pattern: "DL-\\d{4}-\\d{5}"
        description: "DVLA reference number"
    - status:
        contains: "application received"
    - name:
        matches: "user_full_name"
    - new_licence:
        contains: "new photocard"
    - timeline:
        contains: "week"

failure_patterns:
  - contains: "cannot renew online"
    action: "switch to post_office"
  - contains: "name changed"
    action: "must_apply_by_post"
  - contains: "signature changed"
    action: "must_apply_by_post"
  - contains: "medical"
    action: "user_handoff"

verification:
  method: "compare_fields"
  confidence: 0.95
  evidence: "screenshot + reference number"
```

### 2. Register to vote

```yaml
step: electoral.register.submit
method: online
url: https://www.gov.uk/register-to-vote

expected_receipt:
  type: confirmation_page
  fields:
    - reference:
        pattern: "VR-\\d+"
        description: "Electoral registration reference"
    - status:
        contains: "registered"
    - name:
        matches: "user_full_name"
    - address:
        matches: "target_address"

failure_patterns:
  - contains: "not eligible"
    action: "inform_user"
  - contains: "already registered"
    action: "idempotent_success"

verification:
  method: "compare_fields"
  confidence: 0.95
  evidence: "confirmation page"
```

### 3. Check MOT history

```yaml
step: dvsa.mot.lookup
method: online
url: https://www.gov.uk/check-mot-history

expected_receipt:
  type: results_page
  fields:
    - registration:
        matches: "vehicle_registration"
    - make:
        exists: true
    - model:
        exists: true
    - mot_status:
        one_of: ["pass", "fail", "no_mot"]
    - mot_expiry:
        pattern: "\\d{2}/\\d{2}/\\d{4}"
    - tests:
        type: array
        items:
          - date: { pattern: "\\d{2}/\\d{2}/\\d{4}" }
            result: { one_of: ["PASS", "FAIL", "ADVISORY", "PRS"] }
            mileage: { pattern: "\\d+" }

failure_patterns:
  - contains: "no record"
    action: "check_registration"
  - contains: "not found"
    action: "verify_vehicle_details"

verification:
  method: "schema_match"
  confidence: 0.99
  evidence: "results page data"
```

### 4. Vehicle tax

```yaml
step: dvla.tax.submit
method: online
url: https://www.gov.uk/vehicle-tax

expected_receipt:
  type: confirmation_page
  fields:
    - vehicle_registration:
        matches: "vehicle_registration"
    - tax_status:
        one_of: ["taxed", "SORN"]
    - tax_due:
        pattern: "\\d{2}/\\d{2}/\\d{4}"
    - payment_method:
        one_of: ["direct_debit", "card"]
    - amount:
        pattern: "£\\d+\\.?\\d*"

failure_patterns:
  - contains: "no reference"
    action: "need_dvla_reminder_or_v5c"
  - contains: "expired"
    action: "user_handoff"
  - contains: "SORN"
    action: "confirm_sorn_intended"

verification:
  method: "compare_fields"
  confidence: 0.95
  evidence: "confirmation page"
```

### 5. Council tax band

```yaml
step: council_tax.lookup
method: online
url: https://www.gov.uk/council-tax-bands

expected_receipt:
  type: results_page
  fields:
    - address:
        matches: "target_address"
    - band:
        one_of: ["A","B","C","D","E","F","G","H"]
    - council:
        exists: true
    - annual_amount:
        pattern: "£\\d+[\\d,]*"

failure_patterns:
  - contains: "scotland"
    action: "use_saa_gov_uk_instead"
  - contains: "not found"
    action: "check_postcode"

verification:
  method: "compare_fields"
  confidence: 0.99
  evidence: "lookup result"
```

### 6. Companies House — check company

```yaml
step: companies_house.lookup
method: api
url: "https://api.company-information.service.gov.uk/company/{number}"

expected_receipt:
  type: api_response
  fields:
    - company_number:
        matches: "target_number"
    - company_name:
        exists: true
    - status:
        one_of: ["active", "dissolved", "liquidation", "administration"]
    - incorporation_date:
        pattern: "\\d{4}-\\d{2}-\\d{2}"
    - sic_codes:
        type: array
        items: { pattern: "\\d{5}" }

verification:
  method: "api_match"
  confidence: 0.99
  evidence: "API response"
```

### 7. Council — report missed bin

```yaml
step: council.report_missed_bin
method: online
url: "{council_url}/report-missed-collection"

expected_receipt:
  type: confirmation_page
  fields:
    - reference:
        exists: true
    - collection_type:
        one_of: ["general_waste", "recycling", "food_waste", "garden_waste"]
    - next_collection:
        pattern: "\\d{1,2}\\s+\\w+\\s+\\d{4}"
    - status:
        contains: "reported"

verification:
  method: "compare_fields"
  confidence: 0.85
  evidence: "confirmation page"
  notes: "Council websites vary significantly"
```

### 8. Council — parking permit

```yaml
step: council.parking_permit
method: online
url: "{council_url}/parking/permits"

expected_receipt:
  type: application_confirmation
  fields:
    - application_reference:
        exists: true
    - vehicle_registration:
        matches: "vehicle_registration"
    - zone:
        exists: true
    - cost:
        pattern: "£\\d+"
    - status:
        contains: "application"

verification:
  method: "compare_fields"
  confidence: 0.80
  evidence: "application confirmation"
  notes: "Approval may be delayed"
```

## How Muse uses receipt patterns

### Before executing a step

```text
1. Load receipt pattern for this step
2. Identify required fields (from pattern.required_fields)
3. Gather information from user/memory
4. Fill form fields
5. Submit
6. Capture confirmation
7. Run QP verification against receipt pattern
8. If PASS → store verified outcome, proceed to next step
9. If FAIL → check failure_patterns for specific action
10. If UNKNOWN → escalate to user
```

### After executing a step

```text
Muse captures: confirmation page HTML/text

QP verifies:
  - reference matches pattern? ✓
  - status matches expected? ✓
  - fields present? ✓
  - no failure patterns matched? ✓

Result:
  truth_class: VERIFIED
  evidence: "confirmation screenshot + reference number"
  receipt: { reference: "DL-2026-12345", status: "application_received" }
```

## The garden grows

Every verified receipt teaches us:

```text
receipt_pattern:
  version: 3
  last_verified: 2026-09-19
  success_rate: 0.95
  common_failures:
    - pattern: "name changed"
      frequency: 12%
      action: "switch to post"
    - pattern: "signature changed"
      frequency: 3%
      action: "switch to post office"
```

After 1000 verifications, we know:
- Which steps reliably work
- Which ones fail often
- What the failure patterns look like
- When to escalate vs retry

That's the garden moat.
