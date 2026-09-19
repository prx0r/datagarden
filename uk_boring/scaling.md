# UK Boring — The Scaling Architecture

## The insight

Most UK administrative workflows are **national** with **local overrides**.

```text
move_home:
  80% national (DVLA, HMRC, electoral, vehicle tax)
  20% local (council tax, waste, parking, planning)

renew_licence:
  100% national (DVLA)

register_to_vote:
  90% national (GOV.UK)
  10% local (council processes)

check_mot:
  100% national (DVSA)
```

So the architecture is:

```text
national_primitive
        ↓
nation_rules
        ↓
service_family
        ↓
local_override
        ↓
UPRN_context
        ↓
individual_state
```

## The scaling formula

```text
1 national workflow (move_home)
  × 400 councils
  × local overrides
  = 400 localized workflows
  from ONE implementation
```

The national layer is the big win. Local overrides are the garden data.

## What changes per council

| Component | National | Local |
|-----------|----------|-------|
| DVLA address | ✓ identical | — |
| HMRC address | ✓ identical | — |
| Electoral | ✓ identical | — |
| Vehicle tax | ✓ identical | — |
| Council tax | — | council URL, forms, references |
| Waste/bin | — | collection days, bin types |
| Parking | — | zones, prices, application process |
| Planning | — | portal, search, applications |

## What stays the same everywhere

| Component | Why |
|-----------|-----|
| DVLA workflow | Same GOV.UK form everywhere |
| Electoral | Same GOV.UK form everywhere |
| HMRC | Same GOV.UK portal everywhere |
| Vehicle tax | Same GOV.UK form everywhere |
| Receipt patterns | Same confirmation format |
| Action classes | Same AUTO/APPROVAL/USER_HANDOFF |
| QP verification | Same evidence → claim → receipt |

## The place object becomes a config

```text
Place
  ├── national_workflows (inherited)
  │   ├── dvla.address_change
  │   ├── electoral.register
  │   ├── hmrc.address_change
  │   └── vehicle_tax.address_change
  │
  └── local_workflows (overridden)
      ├── council_tax.move_home (council-specific)
      ├── waste.missed_bin (council-specific)
      ├── parking.permit (council-specific)
      └── planning.search (council-specific)
```

A new city = new config, same national primitives.
