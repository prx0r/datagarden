# Boring UK — The Workflow Garden (Sharpened)

## The boundary

> **If a good answer can end as prose, Boring UK should not build it.**
> **If the user still has 4 websites, 3 forms, 2 logins, a deadline and a confirmation number left after the answer, that is Boring UK territory.**

GOV.UK already launched GOV.UK Chat in May 2026 to answer questions about government services. GDS is now exploring agentic AI for completing tasks. One Login covers 200+ services, passkeys rolling out to 23M users.

**Boring UK should not compete on "tell me how government works."** That layer is getting eaten.

The valuable gap:

> **Take a messy real-life UK situation that crosses several organisations, and reliably move it toward DONE.**

## Life states, not individual forms

| Parent capability | What user says | Children | Why it survives |
|---|---|---|---|
| **Council MCP** | "Sort this council thing out." | council tax, parking, bins, bulky waste, licences, planning, missed collections, discounts | Extremely fragmented locally. GOV.UK just takes postcode → find your council. |
| **Move UK** | "I'm moving next Friday. Handle the admin." | DVLA, V5C, tax DD, HMRC, council tax, parking, utilities, broadband, mail, insurers | Crosses government + councils + private. Differentiation is execution/state. |
| **Microbusiness Operator** | "Keep my tiny business legal." | sole trader, deadlines, Companies House, address changes, confirmation statement, tax, permits | Long-lived relationship. Companies House + HMRC have real APIs. |
| **UK Letter Resolver** | "What the hell is this letter? Deal with it." | identify → deadline → action → workflow → track completion | Universal entry point. Muse vision + our tested workflows. |
| **Car Lifecycle** | "I bought this car. Sort everything." | checks, MOT, recall, tax, V5C, insurance, CAZ, servicing, sale | Must execute workflows, not just display dates (Lloyds etc already do reminders). |
| **Family Admin** | "Keep childcare/admin sorted." | eligibility, childcare account, free-hours, reconfirmations, school transitions | Recurring pain: Tax-Free Childcare requires reconfirming every 3 months. |
| **Start Driving** | "Get me from nothing to driving." | provisional, theory, instructor, insurance, practical test, vehicle onboarding | Young-consumer workflow with months of state + commercial referrals. |

## Council MCP — the one that gets more interesting

Britain has different local-government structures. Responsibilities differ between county, district and unitary authorities. GOV.UK takes postcode → find council.

We normalise an ugly national surface into:

```text
council.resolve(postcode)

council.get_bin_day()
council.report_missed_bin()
council.order_bin()
council.book_bulky_waste()

council.get_council_tax()
council.change_address()
council.apply_discount()

council.get_parking_permit()
council.renew_parking_permit()

council.lookup_planning()
council.submit_report()
```

The moat:

```text
Manchester parking permit workflow
        │
        ├─ official endpoint
        ├─ required fields
        ├─ authentication
        ├─ documents
        ├─ fees
        ├─ AUTO / APPROVAL / HANDOFF
        ├─ common failure states
        ├─ completion evidence
        ├─ last verified
        └─ historical execution traces
```

When the council changes its website, an execution fails, we fix the adapter, and **every future agent benefits**. Significantly harder to reproduce by asking a frontier model.

## resolve_letter() — the front door

```text
PHOTO / EMAIL / PDF

"We need you to..."
        ↓
        JEV
classify workflow
        ↓
Boring UK graph

authority = DVLA
intent = update keeper details
deadline = ...
required_state = ...
        ↓
Muse

"I can do steps 1–3.
I need you for identity confirmation at step 4.
Then I'll continue."
```

The user doesn't even need to know which service exists. They just throw bureaucracy at Muse: "Deal with this."

## What NOT to build

```text
❌ UK admin checklist
❌ MOT reminder app
❌ GOV.UK Q&A
❌ moving checklist
❌ "AI tells you what form to fill"
```

## What to build

```text
✓ persistent state
✓ execute steps
✓ know exact handoff boundary
✓ resume afterwards
✓ verify completion
✓ adapt to each council/service
✓ maintain workflow when websites change
```

## The four gardens accumulate different things

```text
POWPOWPOW    accumulates observations
BREADUP      accumulates transactions
UKGRAPH      accumulates economic changes/constraints
BORING UK    accumulates successful executions
```

## The tree

```text
                    BORING UK
                        │
       ┌────────────────┼────────────────┐
       │                │                │
     MOVE              CAR           BUSINESS
       │                │                │
       ├─ council       ├─ buy           ├─ start
       ├─ DVLA          ├─ own           ├─ maintain
       ├─ HMRC          ├─ renew         ├─ file
       └─ utilities     └─ sell          └─ close

              FAMILY        LOCAL
                 │             │
             childcare      council
             school         parking
             admin          waste
                            permits
```

## First research cluster

**Council MCP + resolve_letter() + move_house()**

Map the workflows. See how much can actually be normalized. The position worth occupying:

> "Oh yeah, just give Muse the Boring UK connector. It knows how all that shit works."

## Sources

- GOV.UK Chat: https://www.gov.uk/government/news/millions-to-get-faster-easier-access-to-government-support-with-new-ai-tool
- Council parking permits: https://www.gov.uk/parking-permit
- Moveinout (competition): https://www.moveinout.co.uk/
- Companies House API: https://developer.company-information.service.gov.uk/api-testing
- Used car checks: https://www.gov.uk/checks-when-buying-a-used-car
- Tax-Free Childcare: https://www.gov.uk/tax-free-childcare
- Council types: https://www.gov.uk/understand-how-your-council-works
