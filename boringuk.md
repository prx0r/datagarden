# Boring UK — The Workflow Garden

> **Don't tell me how to do British life admin. Get me as close to done as you're legally and technically allowed to.**

## The sharp rule

> **If a good answer can end as prose, Boring UK should not build it.**
> **If the user still has 4 websites, 3 forms, 2 logins, a deadline and a confirmation number left after the answer, that is Boring UK territory.**

## It's not a data garden. It's a workflow garden.

```text
ChatGPT / generic model
"What do I need to do?"
          ↓
       KNOWLEDGE

Boring UK
"Get this done."
          ↓
retrieve official rules
          ↓
inspect user's state
          ↓
construct exact workflow
          ↓
Muse executes what it can
          ↓
human handoff where required
          ↓
verify completion
          ↓
remember resulting state
```

## The proprietary data that grows

```text
TASK
move house

official workflow version
actual pages encountered
authentication required
documents requested
agent-safe steps
human-only steps
failure reasons
weird edge cases
completion time
confirmation evidence
follow-up deadlines
service changed since last run?
```

After 100,000 executions, you're not merely indexing GOV.UK. You have a continuously tested map of **how Britain actually gets things done**.

## The capability filter

| Level | Example | Build? |
|-------|---------|--------|
| **0 — Answer** | "How much does a passport cost?" | No. ChatGPT/search handles it. |
| **1 — Explain** | "How do I become a sole trader?" | Mostly no. |
| **2 — Prepare** | "Work out exactly what I need and get everything ready." | Maybe. |
| **3 — Execute** | "Update my address everywhere." | **Yes.** |
| **4 — Maintain** | "Keep my car/company/admin compliant." | **Very yes.** |
| **5 — Orchestrate** | "I'm moving house next month; handle the admin." | **Best category.** |

Level 4–5 is where the actual product lives.

## GOV.UK One Login

More than 200 services accessible by February 2026. HMRC migrating onto it. Companies House made One Login the main sign-in route for new users in August 2026. Not universal yet, but authentication is consolidating.

## The strongest capability ideas

| What someone says to Muse | Why this is genuinely agentic | Capability |
|---|---|---|
| "I'm moving house next Friday. Sort everything." | DVLA licence + V5C + vehicle-tax DD + HMRC + council + utilities + broadband + permits; dependencies and timing | `move_house()` |
| "Keep my car legal and tell me only when you need me." | MOT status/history, tax, renewals, recalls, deadlines, bookings | `manage_car()` |
| "I just bought this used car. Do everything I need to do." | Vehicle checks → MOT history → tax → V5C workflow → insurance handoff → reminders | `onboard_car()` |
| "Set me up as a sole trader properly." | Determine registration path → Self Assessment → records → deadlines → ongoing state | `start_sole_trader()` |
| "Keep my little business compliant." | Companies House/HMRC deadlines, confirmation statements, filings, identity state | `manage_business()` |
| "I've changed my name/address. Fix it everywhere." | Find every relevant stateful service, execute updates, track incomplete ones | `change_details_everywhere()` |
| "My passport expires soon. Sort it." | Gather photo/docs → application → payment approval → track completion | `renew_passport()` |
| "I turn 17 next month. Get me ready to drive." | provisional → theory → instructor → tests → car admin; explicit handoffs | `start_driving()` |
| "I'm starting a food business from home. Make me legal." | business type + local authority + registration/licences + tax + insurance | `start_regulated_business()` |
| "I've got this government letter. Deal with whatever it wants." | Vision/document parse → identify authority/task → deadline → exact workflow → execute/handoff | `resolve_letter()` |
| "What boring stuff am I forgetting?" | persistent life-state + deadlines + missing renewals | `admin_audit()` |
| "Take care of everything expiring in the next 60 days." | monitoring + scheduled action + approval | `renewals()` |

## Cars are the ideal first vertical

```text
registration
    ↓
vehicle identity
    ↓
MOT history        ← official API (DVSA, back to 2005)
    ↓
MOT expiry
tax state
V5C state
keeper/address
insurance handoff
recalls
purchase/sale events
    ↓
persistent vehicle state
```

> "Muse, look after my car."

## `resolve_letter()` could be quietly enormous

User photographs any government letter. Then:

```text
document
   ↓
"What is this?"
   ↓
authority / deadline / required response / consequences
   ↓
match tested workflow
   ↓
Muse opens correct service
   ↓
prefills / gathers / executes
   ↓
USER APPROVAL
   ↓
submit where permitted
   ↓
store receipt + next date
```

## Don't automate everything

Encode every action as:

```text
AUTO
APPROVAL_REQUIRED
USER_HANDOFF
UNSUPPORTED
```

Since May 2026 DVSA says car driving-test candidates must book/change/cancel their own test. So:

```text
Muse:
✓ finds correct service
✓ knows what you'll need
✓ helps choose test centre
✓ prepares you
✓ opens exact page
✓ reminds you

USER:
→ completes protected booking step

Muse:
✓ records booking
✓ adds reminders
✓ manages surrounding workflow
```

## Jev's role

Use deterministic rules for:
- deadline
- eligibility requirement
- required document
- legal restriction
- fee
- official endpoint

Use Jev for messy classification:
- "What kind of letter is this?"
- "Which workflow most likely matches this user's situation?"
- "Is sufficient information available to continue?"
- "Does this execution look anomalous enough to require human review?"

**Jev routes. It doesn't invent British administrative rules.**

## The four gardens

```text
UKGraph
= Britain as an economic graph
= WHERE IS THE OPPORTUNITY?

Boring UK
= Britain as an executable workflow graph
= HOW DO I GET THE THING DONE?

Breadup
= physical-object economics
= WHAT IS THIS WORTH?

PowPowPow
= compute-resource economics
= WHAT CAN THIS HARDWARE DO?
```

## YouTube content

- "I Gave an AI 20 Annoying UK Government Letters"
- "Can AI Actually Sort Out Your DVLA Admin?"
- "I Asked Muse to Move House in Britain — Here's What It Could Really Do"
- "How Much of Starting a UK Business Can AI Do For You?"

The videos test the capability. Failures become garden data. Comments reveal the next workflow people want.

## Sources

- GOV.UK One Login: https://www.gov.uk/government/news/hmrc-introduces-govukonelogin-for-new-customers
- MOT History API: https://documentation.history.mot.api.gov.uk/
- Muse announcement: https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/
- DVSA booking rules: https://www.gov.uk/book-driving-test
- Change driving licence address: https://www.gov.uk/change-address-driving-licence
- Self Assessment registration: https://www.gov.uk/register-for-self-assessment
