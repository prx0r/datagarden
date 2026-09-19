# UKGraph — Final Architecture

## Naming

```
UKGRAPH = the whole datagarden
├── UKBoring = workflows + actions + receipts (formerly UK Admin)
├── UKOpportunity = signals + jobs + tenders + grants (formerly UKGraph economic)
└── UKProducts = markets + products + prices (formerly Breadup)
```

## The downstream signal

Meta has: user history, calendar, email, social connections, purchase patterns.

We have: economic ground truth, local market data, verified workflows, outcome history.

Together:

```
"You have rare skills based on:
 - your qualification in X
 - your experience with Y
 - your location in Oldham
 - local demand data showing Z is scarce
 - 3 employers currently hiring for this
 - training grant available for certification

We think you should:
 1. Apply for the EV installer role at [company]
 2. Get the QNCE certification (grant covers cost)
 3. Side income: repair and flip used chargers (40% margin)

Want me to:
 - Start the application?
 - Book the training?
 - List your first charger for sale?"
```

That's not possible without:
- Personal context (Meta provides)
- Economic ground truth (we provide)
- Verified workflows (UKBoring provides)
- Outcome history (garden provides)

## The beautiful feedback loop

```
Jeff uses UKBoring to renew his licence
    ↓
Garden knows: Jeff is a qualified electrician in Oldham
    ↓
UKOpportunity sees: 3 EV install jobs in Oldham
    ↓
Muse says: "Jeff, based on your skills and local demand,
           here's how to make £500 this weekend"
    ↓
Jeff takes the job
    ↓
Outcome verified
    ↓
Garden knows: electrician + Oldham + EV = money
    ↓
Next person with similar skills gets the same recommendation
    ↓
Garden grows
```

## The four gardens (final)

```
UKGRAPH
├── UKBoring      "I am lazy" → do it for me
├── UKOpportunity "I want money" → show me how
├── UKProducts    "What's this worth?" → price it
└── (shared)      Place, Goal, Workflow, Evidence, Outcome
```

## The three principles in action

```
"I AM LAZY"
  → UKBoring handles the admin
  → Muse executes workflows
  → User does nothing

"I WANT MONEY"
  → UKOpportunity finds opportunities
  → Matches skills to local demand
  → Shows concrete next steps

"I AM AN IDIOT"
  → Dead simple interface
  → "Do you want me to do this? Yes/No"
  → No learning required
```

## The product

Not a database. Not an API. Not a chatbot.

The product is:

> "Given everything we know about you and everything we know about Britain,
> here is exactly what you should do next to make your life better."

That's it.
