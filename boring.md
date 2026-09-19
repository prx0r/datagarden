# UK Admin — How Do I Actually Get This Boring UK Thing Done?

## The primitive

```text
UKGRAPH = understand Britain
UK ADMIN = get boring British things done
```

The asset is a continually updated **UK action graph**:

```text
"I need to do X"
       ↓
jurisdiction
       ↓
eligibility
       ↓
prerequisites
       ↓
documents required
       ↓
identity/authentication
       ↓
official service
       ↓
CAN AGENT DO IT?
 ┌────────┼─────────┐
 yes     assist   user-only
 └────────┼─────────┘
          ↓
fees / deadlines / waiting times
          ↓
confirmation / proof
          ↓
next action
```

## Every capability has a structured record

```text
task: renew_driving_licence
authority: DVLA
jurisdiction: GB

requires:
- identity
- licence details
- address

agent_permissions:
- explain: yes
- gather requirements: yes
- prefill: maybe
- submit: depends on service/auth
- payment: explicit approval
- retain credentials: no

failure_modes:
- identity mismatch
- address mismatch
- expired documents

official_source:
- ...

last_verified:
- 2026-09-19
```

This is **agent infrastructure**, not content.

## The garden knows where the boundary is

Since May 2026, DVSA explicitly says a car candidate **must book, change, swap or cancel their own test**, and that booking for someone else is against the law.

A bullshit generic agent says: "Sure, I'll book your test."

Our UK Admin garden returns:

```text
ACTION CLASS: USER_ONLY

Muse may:
✓ identify appropriate test centres
✓ explain release/cancellation mechanics
✓ collect the information you'll need
✓ remind you
✓ take you to the correct official service

Muse must hand control to user for:
✗ booking
✗ changing
✗ cancelling
```

That's a feature. The garden gives Muse reliable knowledge about what it *can* do.

## The four gardens

```text
POWPOWPOW
"What can my compute do?"

BREADUP
"What is this physical thing worth?"

UKGRAPH
"Where are Britain's economic opportunities/constraints?"

UK ADMIN
"How do I actually get this boring UK thing done?"
```

## Killer natural-language capabilities

| Person says to Muse | UK Admin capability |
|---|---|
| "Sort out my passport renewal." | `prepare_passport_renewal()` |
| "My driving licence expires soon, deal with it." | `renew_driving_licence()` |
| "When does my MOT run out and what do I need to do?" | `manage_mot()` |
| "I've moved house. What UK stuff do I need to update?" | `moving_house_checklist()` |
| "Set me up as a sole trader." | `start_sole_trader()` |
| "Tell me what I need to file this year." | `tax_obligations()` |
| "I want to start selling online. What do I legally need?" | `start_online_business()` |
| "Can I get any childcare support?" | `check_childcare_support()` |
| "I'm having a baby. What government things do I need to do?" | `new_parent_admin()` |
| "I lost my passport." | `lost_passport()` |
| "I'm buying a used car. Check everything." | `used_car_checks()` |
| "I'm moving to Manchester next month. Sort the admin." | `relocation_admin()` |
| "Set up a company for this side project." | `company_setup()` |
| "I got this weird council letter — what do I actually have to do?" | `resolve_gov_letter()` |
| "What benefits/support might I actually qualify for?" | `support_check()` |

## Many become lifelong state machines

```text
CAR
├── tax
├── MOT
├── insurance
├── licence
├── parking permits
├── congestion / clean-air rules
└── renewal dates

BUSINESS
├── Companies House
├── HMRC
├── VAT threshold
├── self assessment
├── payroll
├── licences
└── filing dates

HOME
├── council tax
├── utilities
├── electoral register
├── parking
└── address changes
```

## The connector proposition

> "Muse, keep my UK life admin sorted."

That's a strong consumer proposition.

## Affiliate transition

```text
"I need an MOT"
     ↓
official requirements/check
     ↓
nearby garages

"I need to learn to drive"
     ↓
provisional/licence/test process
     ↓
driving instructors

"I'm starting as a sole trader"
     ↓
HMRC setup
     ↓
accounting software
business bank account
insurance
website
payment processor

"I'm moving house"
     ↓
government address changes
     ↓
broadband
energy
removals
insurance
```

Commercial recommendation occurs exactly when the user's intent exists.

## Connection to UKGraph

Keep them separate, but let them join.

UKGraph discovers:
```text
Manchester
↓
driving instructors increasingly constrained
↓
prices rising
↓
new-driver population growing
```

UK Admin knows:
```text
how to become an instructor
requirements
qualification sequence
fees
registration
official applications
```

Muse asks: "How can I make more money?"

UKGraph: "ADI supply appears constrained around you."

UK Admin: "Here is exactly what becoming one entails."

Muse: "Given your situation, here's the process and the parts I can handle."

## The boring category is the moat

Thousands of AI developers will build:
- AI influencer
- AI video generator
- AI trading copilot
- AI productivity assistant

Far fewer will get excited about:
- "Correctly handle a UK vehicle keeper address change and know exactly where the user needs to take over."

Yet the latter has:
- Clear intent
- Objectively correct outcome
- Authoritative data
- Enormous recurring population
- Measurable completion

That is almost perfect gardening territory.

## The rule for new software ideas

If UKGraph reveals some boring recurring pain like "thousands of people struggle with X government/business process", don't automatically make a startup.

First ask: **Could this simply become another superpower inside the UK connector?**

## Sources

- GOV.UK One Login: https://www.gov.uk/government/news/hmrc-introduces-govukonelogin-for-new-customers
- DVSA booking rules: https://www.gov.uk/book-driving-test
- GOV.UK APIs: https://www.api.gov.uk/
- Companies House API: https://developer.company-information.service.gov.uk/
- Nomis API: https://www.nomisweb.co.uk/api/v01/help
