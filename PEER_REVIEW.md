# Peer Review — Critical Fixes

## P0.1: Stop emitting awarded contracts as live bid opportunities

The contracts collector requests `status: Awarded` and stores `awardedValue`, `awardedSupplier`.
`_find_contracts()` turns these into `action=BID_CONTRACT`.

**Fix:** Split into:
- `PROCUREMENT_OPPORTUNITY` (live, future, open) — can emit as route
- `PROCUREMENT_AWARD` (historical) — useful for intelligence only

**Rule:** No route with action=BID_CONTRACT may derive only from an Awarded notice.

## P0.2: Planning collector doesn't collect "recent" or "Oldham"

The collector fetches first entity results without place/temporal filters.

**Fix:** Add LPA filter, temporal cursor, preserve entity IDs.

## P0.3: Demo claims leaking into live output

`_find_upgrades()` emits "EV charger demand up 31%" with no provenance.

**Fix:** Remove all unsupported market_analysis opportunities. Every factual claim needs observation IDs.

## P0.4: Expected economic value is fabricated

"£500", "30% margin", "£30-80 repair" — demo heuristics presented as sourced.

**Fix:** Every economic number needs a METHOD. If no defensible estimate: `expected_value = UNKNOWN`.

## P0.5: Exception swallowing

`except Exception: pass` silently hides broken collectors.

**Fix:** Typed failures: SOURCE_UNAVAILABLE, SCHEMA_CHANGED, NORMALIZATION_FAILED, STALE_DATA.

## P1.1: Duplicate canonical models

`uk_boring/earn.py` defines its own CapabilityEnvelope and Opportunity. `core/` has Route.

**Fix:** Import from core. One type per concept.

## P1.2: Observation IDs collide

Current IDs based on identity fields, not observation events.

**Fix:** Separate series_key (what) from observation_id (when).

## P1.3: JSONL in Git doesn't scale

**Fix:** JSONL as dev fixture only. Production: Postgres + object storage.

## P1.4: Source licensing vague

"transformative use" is not a licence.

**Fix:** Every source needs: legal owner, licence, allowed retention, required attribution.

## P2: One connector outward

Six MCP servers + 86 tools = confusion.

**Fix:** One UKGraph MCP with earn/do/value/find/watch.

## P3: Rebuild earn() around real routes

Current earn() is a prototype with fabricated values.

**Fix:** Separate route generators:
- paid_work (live jobs/gigs)
- live_procurement (active opportunities)
- products/flips (acquisition → margin)
- planning_derived_demand (signals, not jobs)
- upgrade/training (unlocking capacity)

## P4: Route contract

Every Route needs:
- Identity + action + target
- Fit (capabilities, constraints)
- Economics (value, method, uncertainty)
- Evidence (observation IDs, sources, freshness)
- Lineage (transforms, DecisionSpecs)
- Proof (what counts as success)
- Quality (separate confidence dimensions)

## P5: No magic confidence score

Track separate confidences:
- source confidence
- entity match confidence
- capability fit confidence
- economic estimate confidence
- availability confidence

## P6: Jev integration

First DecisionSpecs:
- opportunity.capability_family.v1
- opportunity.sole_trader_access.v1
- planning.implied_trade_demand.v1

Every Jev call must store: spec ID, version, output distribution, answer, confidence, fallback, source obs IDs.

## P7: QP-lite must be real settlement

- receipt.settle() must require proof execution
- ProofRule: id, version, claim_type, predicate, source_requirements
- EvidenceArtifact: artifact_id, type, issuer, captured_at, hash
- No manual TRUE without proof

## P8: Don't model volatile form UIs

UKBoring maintains: goal, authority, entrypoint, rules, evidence, failure conditions.
NOT: selectors, every form field, every page step.

## P9: Move-home → test fixture

Until each step has: source, jurisdiction, version, proof rule, validation test.

## P10: Documentation cleanup

Canonical docs: README, SPEC, DEV, OPERATIONS, GARDENS, DECISIONS, CHANGELOG.
Archive superseded docs.

## P11: pyproject + lock

Replace requirements.txt.

## P12: CI missing

Add .github/workflows with: compileall, ruff, pytest, fixture tests.

## P13: Tests need semantic invariants

Not just shapes. Need:
- awarded_contract_never_emits_bid_route
- route_requires_evidence
- missing_data_is_unknown_not_false
- receipt_cannot_be_true_without_proof

## P14: First real benchmark

"I'm in Oldham, electrician, Saturday free, £500. Make £300."
Three route families: WORK, PUBLIC_OPPORTUNITY, PRODUCT_ECONOMICS.
Each with: evidence, freshness, economic method, uncertainties.

## P15: Historical data is the first moat

Contracts and planning are reconstructable. UKProducts/Breadup with disappearing listings and historical sold prices is where time matters first.
