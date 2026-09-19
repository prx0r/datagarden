# Complaints Data → Structured Workflows

## The insight

Every complaint is someone who:
- Tried to do something
- Failed
- Had to spend time complaining

If we can prevent that failure, we save people time AND generate verified outcomes.

## The data we can get (all free)

| Source | What | Records | API |
|--------|------|---------|-----|
| DWP complaints | Universal Credit, Child Maintenance | 8K/quarter | Published CSV |
| Local Gov Ombudsman | Council complaints by LA | 20K+/year | CSV/XLSX |
| Council complaints | Per-council volumes | Varies | Published reports |
| Housing Ombudsman | Housing complaints | Annual | CSV/XLSX |
| Citizens Advice | Consumer complaint types | 290K/year | Published stats |

## How to structure it

### Raw complaints → Canonical observations

```python
{
    "observation_id": "hash",
    "garden": "ukadmin",
    "source_id": "dwp_complaints",
    "metric": "complaint_volume",
    "entity_type": "service",
    "entity_ref": "universal_credit",
    "value": {
        "quarter": "2025-Q3",
        "complaints_received": 8005,
        "complaints_closed": 6730,
        "upheld_rate": 0.4,
        "top_reason": "You've got it wrong",
    },
    "truth_class": "KNOWN"
}
```

### Complaints → Workflow improvements

```
DWP: "You've got it wrong" = 3,655/quarter
  → Universal Credit has the most errors
  → Workflow should verify eligibility BEFORE submission
  → Add eligibility check step to move_home workflow

Council: Housing repairs = 67% of complaints
  → Repair workflows need better evidence collection
  → Add photo requirement to maintenance requests

Citizens Advice: Used cars = 17.8% of complaints
  → Car purchase workflow needs better verification
  → Add VIN check step to used_car workflow
```

### Complaints → Opportunity signals

```
High complaint rate in area X
  → Council service is struggling
  → Opportunity for: consultant, trainer, process improvement
  → UKOpportunity: "Council X needs help with Y"

Rising complaint trend
  → Service degrading
  → Opportunity for: automation, outsourcing, new provider
  → UKOpportunity: "Market gap in Z"

Low complaint rate
  → Service working well
  → Learn from their processes
  → UKOpportunity: "Best practice model in W"
```

## The structured data model

```python
@dataclass
class ComplaintPattern:
    """A pattern of complaints for a service."""
    service: str
    authority: str
    period: str
    complaints_received: int
    complaints_closed: int
    upheld_rate: float
    top_reasons: list
    corrective_actions: list
    trend: str  # improving, stable, worsening
    confidence: float
    source: str
    observed_at: str

@dataclass
class WorkflowFailure:
    """A specific failure mode in a workflow."""
    workflow_id: str
    failure_type: str
    frequency: float  # % of complaints
    corrective_action: str
    suggested_improvement: str
    source: str
    observed_at: str
```

## How it feeds the earn system

```
Complaint: "Housing repairs = 67% of complaints in RBKC"
    ↓
UKOpportunity signal: "RBKC needs housing repair improvement"
    ↓
UKAdmin: "Add photo requirement to maintenance workflow"
    ↓
Muse: "Before submitting a repair request, take a photo of the damage"
    ↓
Fewer complaints → verified outcomes → garden grows
```

## The money angle

```
Complaint = someone spent time failing
    ↓
Prevent failure = save people time
    ↓
Save time = generate verified outcomes
    ↓
Verified outcomes = garden growing
    ↓
Garden growing = more useful routes
    ↓
More useful routes = more Muse usage
    ↓
More Muse usage = more data
    ↓
More data = better garden
```

## What to build NOW

1. **Download DWP complaints CSV** — free, quarterly, structured
2. **Download Local Gov Ombudsman CSV** — free, annual, per-council
3. **Normalize into canonical complaints** — store in ukadmin garden
4. **Map complaints to workflows** — which workflow would prevent this?
5. **Add complaint patterns to workflow schemas** — "if this complaint type, add this step"

This is the boring stuff that makes UKGraph genuinely useful.
