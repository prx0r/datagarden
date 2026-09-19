# PR5 — Truth/Integrity Hardening

## The diagnosis

The thesis is strong. The implementation is currently **too optimistic about how much is "real"**. PowPowPow is the right exemplar because it starts from observable reality and derives capabilities; datagarden has started doing the reverse — declaring useful-looking MCP tools and filling gaps with heuristics.

The immediate priority is **truth/integrity hardening, not adding another garden or another 20 tools**.

## What is already excellent

**CANONICAL.md** — "The unit of planning is the human sentence, not the project." Exactly the right product rule.

**formula.md** — Timestamps alone are not the moat. The stronger asset is the path-dependent loop: data → user response → changed collection strategy → better product.

**Four-garden distinction:**

| Garden | Primitive | Core question |
|--------|-----------|---------------|
| PowPowPow | resource observation | What can this compute do economically? |
| Breadup | object/transaction | What is this physical thing actually worth? |
| UKGraph | economic constraint/change | Where is there room/opportunity? |
| Boring UK | workflow execution | How do I actually get this annoying UK thing done? |

## P0: shared/ isn't actually shared yet

`shared/warehouse.py`, `shared/entities.py`, `shared/manifest.py` still write to `/home/box/powpowpow/warehouse`. A DataGarden collection run manipulates PowPowPow's warehouse, not a generic one.

The daily manifest hashes `/home/box/powpowpow/warehouse`. Breadup and UKGraph data under `forests/...` are not what the Merkle manifest attests to.

`shared/schema.py` header still says "PowPowPow — Universal Chain Schema." Most classes are mining-specific. `BitemporalMixin` exists but observation types don't inherit it.

This is a symptom of extracting **implementation files** when we need to extract the **protocol**.

## P0: Overclaiming capability maturity

Breadup MCP tools don't yet mean what their names imply:
- `find_flips()` — sold price dispersion ≠ acquisition-to-resale margin
- `max_offer()` — no fees, postage, condition mismatch, return probability
- `liquidity_score()` — string test `'2026-09' in date` ≠ seven days
- `repair_vs_sell()` — arbitrary 40%/60% multipliers

Returning `"status": "ok"` as though evidence-backed is wrong.

Introduce **truth class** everywhere:

```text
VERIFIED      — directly measured, provenance clear
DERIVED       — computed from verified observations
ESTIMATED     — computed with assumptions
HEURISTIC     — rule of thumb, not calibrated
CONCEPTUAL    — architecture only, no data
UNAVAILABLE   — data not yet collected
```

## P0: UKGraph needs methodological rewrite

`career_crowding()` derives scores from how many ONS documents mention an occupation. Not economically interpretable.

`business_gap()` counts sector mentions. Postcode doesn't form a geographic denominator.

`salary_data()` has hard-coded salary ranges. Defeats the purpose.

First UKGraph capability should be narrow and correct:

```text
wage_growth(soc_code, region, start_year, end_year)
```

from ASHE occupation × region × year. That's a genuine fact.

## P0: Boring UK verification is the product

Don't stamp a task "verified today" because the row was created today. Each step needs:

```text
valid_from
verified_at
next_verification_at
source_hash/source_url
```

## P0: Common response contract

Every capability returns:

```json
{
  "capability": "breadup.value_listing",
  "as_of": "2026-09-19T08:00:00Z",
  "result": {},
  "truth_class": "DERIVED",
  "confidence": 0.82,
  "evidence": ["observation_id_1"],
  "method": {"id": "breadup_valuation", "version": "0.2.0"},
  "limitations": [],
  "action": {"class": "ADVISORY"}
}
```

Capability output never exists without evidence lineage.

## The six concepts for garden_core

```text
Observation    — raw immutable record from reality
Entity         — permanent thing being observed
Source         — where observations come from (cadence, recoverability, health)
DerivedFact    — computed from observations with method + version
CapabilityResult — answer to a human question with truth_class + evidence
Outcome        — what actually happened after the capability was used
```

## PowPowPow exemplar but needs hardening

- Multiple ingestion architectures alive: warehouse.py, v1_pipeline.py, core.py, collector custom logic
- api.py imports `get_v1_registry()` which doesn't exist in current v1_registry.py
- v1_live_cards.py hardcodes ELECTRICITY = 0.10, parameter not passed through
- Profitability results not yet authoritative

## Manifest bug

`verify_manifest_integrity()` calls `generate_manifest()` which writes to the manifest file. Verification mutates what it's trying to verify. Must be read-only.

## What to do next

1. Make DataGarden a control plane, not a bigger PowPowPow
2. Build garden_core with six concepts
3. Make one source registry
4. Make one capability trustworthy per garden
5. Add outcome objects
6. Add pytest + CI + fixture replay
7. Wire YouTube/Muse feedback only after truth is solid

## The central principle

```text
POWPOWPOW IS A GARDEN
DATAGARDEN IS NOT A BIGGER POWPOWPOW
```

DataGarden is the common **grammar** for growing gardens. PowPowPow is the first successful sentence written in that grammar.
