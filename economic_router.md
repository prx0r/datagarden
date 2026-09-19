# UKGraph — The Economic Router

## The distinction from a job engine

Indeed: `WHAT JOB ARE YOU LOOKING FOR?` → keywords → listings → search results

UKGraph: `WHAT RESOURCES DOES THIS HUMAN HAVE?` → `WHAT ECONOMIC ROUTES CURRENTLY EXIST?` → intersections humans wouldn't formulate as searches

```
Person × Current Economy → Actions
```

## What a human has (that they don't think of as economic data)

```
time
location
skills
qualifications
interests          ← "I love music" → festival work
physical abilities
vehicle
tools
capital
social connections
risk tolerance
things they own
things they enjoy
```

**Preferences become economic features.**

## The iKlean example

```
Tom:
  likes music/festivals
  doesn't mind physical work
  free Aug 27–31
  needs money
  currently in England
  no cleaning qualification

iKlean:
  Creamfields, Aug 27–31
  £12.75/hr, no specialist qualification
  festival environment, application open

Muse:
  "You like festivals and want quick income.
   iKlean is recruiting crew for Creamfields
   27–31 August. No cleaning qualification needed.
   Want me to fill out the application?"
```

Tom never thought to search "festival cleaning operative."

The router finds intersections humans wouldn't formulate as searches.

## The candidate set is wider than "jobs"

```
EMPLOYMENT    iKlean festival shifts
GIG           local EV installation
CONTRACT      council maintenance opportunity
SALE          unused power tool
FLIP          repair/resell appliance
SERVICE       offer weekend PAT testing
ARBITRAGE     local item → national marketplace
TRAINING      certification that unlocks work
REFERRAL      introduce buyer/supplier where permitted
```

All compete for the person's: time, capital, abilities, assets, attention.

Indeed is one **source node** inside that graph.

## The primitive

```text
ukgraph.earn(
    target=£500,
    deadline=7_days,
    person_context=...
)
```

Returns:

```
1. Existing skill job     £310 expected
2. Sell unused equipment  £140 expected
3. Saturday festival shift £102 expected
```

Muse:

> "You need £500 before Friday. The least disruptive route is selling the unused amp plus two evening electrical call-outs. Expected total ~£530. Want me to list the amp and message the two leads?"

## The moat: outcome-conditioned matching

Initially: `Person → opportunity`

Later:
```
Person
× opportunity characteristics
× historical similar people
× verified outcomes
→ expected result
```

Weird second-order facts emerge:

```
Music interest × festival work → 2.1× completion/repeat
Van ownership × furniture resale → much higher realised margin
Electrician × EV work × 15-mile radius → high conversion
Certain tender category × sole trader → terrible win rate
```

These don't exist in any dataset. They emerge from economic activity routed through the system.

## The garden

Every recommendation produces an outcome. Every outcome calibrates future recommendations. The accumulated dataset becomes:

```
who was shown what
who pursued it
who qualified
who won
how much it paid
what predicted success
what disappeared quickly
```

That's gold. Not because the AI is brilliant. Because we can calibrate opportunity signals against real economic outcomes.

## The UX

> Muse: You've got four free days next month and you said you love festivals. There's currently paid work at Creamfields that looks unusually low-friction for you. Want me to apply?

User: yeah

Everything exists to make those two lines **correct often enough to trust**.
