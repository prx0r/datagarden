# Pain Points → Data → AI Stack

## Consumer pain points → UKGraph capabilities

### "I'm moving house"

```
PAIN: 12+ government services to notify, different websites, different logins
DATA: UPRN → council, DVLA, HMRC, electoral, waste, parking
AI:   Jev classifies which steps are automatable
STACK: Muse fills forms, QP verifies receipts, garden stores outcomes
RESULT: "Done. 5 of 7 steps completed. Here are your confirmation numbers."
```

### "What's this area like?"

```
PAIN: No single source for "what is it like to live in Oldham?"
DATA: Economic + planning + services + schools + crime + transport
AI:   Jev synthesizes into human-friendly summary
STACK: Muse calls UKGraph API, presents to user
RESULT: "Oldham has 120 new businesses this quarter, average salary £28.500,
         top growing sectors are healthcare and logistics."
```

### "I need a tradesperson"

```
PAIN: Don't know who's good, don't know fair price, don't know availability
DATA: Local providers + pricing + availability + reviews
AI:   Jev ranks by fit (location, urgency, budget, skill)
STACK: Muse routes to Checkatrade/Taskrabbit/local
RESULT: "3 plumbers available tomorrow. £65-85/hr. Here are their reviews."
```

### "What's changing in my area?"

```
PAIN: Don't know about planning applications, new businesses, regulation changes
DATA: Planning + Companies House + council changes + procurement
AI:   Jev detects significant changes, filters noise
STACK: GeoEvent feed, Muse notifications
RESULT: "12-flat approved on your street. New curry opening nearby.
         Council tax changing in April."
```

### "What should I do about this letter?"

```
PAIN: Confusing government correspondence, don't know deadline or action
DATA: Letter parsing → workflow identification → receipt patterns
AI:   Jev classifies letter type, extracts deadline
STACK: Muse reads letter, identifies workflow, executes or hands off
RESULT: "DVLA needs you to update your address by Oct 15.
         I can do this now. Want me to proceed?"
```

## Business pain points → UKGraph capabilities

### "Where should I open a business?"

```
PAIN: Don't know which area has demand but low competition
DATA: Business formations/closures + planning + wages + skills gaps
AI:   Jev scores areas by opportunity
STACK: UKGraph API returns ranked areas
RESULT: "Nottingham NG7 has high food business demand, low supply,
         3 residential developments approved nearby."
```

### "Where are the skilled workers?"

```
PAIN: Can't find electricians/plumbers in specific areas
DATA: ASHE wages + ONS employment + skills gaps + planning demand
AI:   Jev identifies constrained markets
STACK: UKGraph API returns constraint analysis
RESULT: "Electrician demand-to-supply ratio is 2.3:1 in Manchester.
         Average wage is £38k, rising 8% YoY."
```

### "What contracts are available?"

```
PAIN: Government procurement is fragmented across portals
DATA: Contracts Finder + council procurement + planning obligations
AI:   Jev filters relevant contracts by capability
STACK: UKGraph API aggregates and filters
RESULT: "3 plumbing contracts in Nottingham this quarter.
         Total value: £45k. Deadline: Oct 30."
```

### "What's the competition doing?"

```
PAIN: Don't know which businesses are opening/closing nearby
DATA: Companies House formations/closures + planning + reviews
AI:   Jev detects market shifts
STACK: UKGraph API returns competitive intelligence
RESULT: "15 new cafes opened in NG1 this year, 8 closed.
         Net positive but watch the coffee segment — 3 opened last month."
```

## AI stack per capability

### Data layer
```
Sources: ONS, Land Registry, Companies House, Planning Data,
         Contracts Finder, Checkatrade, postcodes.io
Storage: JSONL canonical format, date-partitioned
Freshness: daily (some real-time)
```

### Decision layer (Jev)
```
Input: raw observations + user context
Output: typed decisions (Choice/Score/Noul)
Use: classify, rank, filter, route
Cost: $0.042/Mtok (output free)
```

### Execution layer (Muse)
```
Input: workflow steps + form data
Output: completed actions + confirmations
Use: fill forms, submit, capture screenshots
Auth: GOV.UK One Login, MFA where required
```

### Verification layer (QP-lite)
```
Input: captured confirmations + receipt patterns
Output: PASS/FAIL/UNKNOWN + evidence
Use: verify outcomes, detect failures
Store: garden history (append-only)
```

### Distribution layer
```
MCP: for agents (Claude, OpenCode, etc.)
API: for developers (JSON, REST)
Muse: for consumers (natural language)
YouTube: for discovery (content → capability)
```

## The formula per pain point

```
PAIN → QUESTION → DATA → JEV DECISION → MUSE ACTION → QP VERIFICATION → GARDEN HISTORY
```

Every pain point follows this formula. The garden grows with every verified outcome.
