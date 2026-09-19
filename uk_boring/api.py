"""UK Boring API — regional intelligence + workflow execution.

Provides:
- Geographic resolution (postcode → place → services)
- Place profiles (economic data, services, workflows)
- Workflow execution with receipt verification
- Outcome tracking
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from datetime import datetime

# Add datagarden to path for boringuk_receipts import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import boringuk_receipts

app = FastAPI(
    title="UK Boring API",
    description="Regional intelligence + workflow execution for UK government services",
    version="0.1.0",
)

# ============================================================
# GEO ENDPOINTS
# ============================================================

@app.get("/api/v1/geo/resolve")
async def geo_resolve(postcode: str = None, uprn: str = None):
    """Resolve a postcode or UPRN to a Place with all jurisdictional overlays."""
    from uk_boring.geo import resolve_postcode

    if postcode:
        place = resolve_postcode(postcode)
        if place:
            return {"status": "ok", "place": place.to_dict()}

    return {"status": "not_found", "message": "Could not resolve location"}

# ============================================================
# AREA ENDPOINTS
# ============================================================

@app.get("/api/v1/areas/{area_id}")
async def get_area(area_id: str):
    """Get area profile."""
    from uk_boring.oldham import OLDHAM, OLDHAM_SERVICES

    if area_id == "oldham":
        return {
            "status": "ok",
            "area": OLDHAM,
            "services": [s["service_id"] for s in OLDHAM_SERVICES],
        }

    raise HTTPException(status_code=404, detail=f"Area {area_id} not found")

@app.get("/api/v1/areas/{area_id}/services")
async def get_area_services(area_id: str):
    """Get available services for an area."""
    from uk_boring.oldham import OLDHAM_SERVICES

    if area_id == "oldham":
        return {"status": "ok", "services": OLDHAM_SERVICES}

    raise HTTPException(status_code=404, detail=f"Area {area_id} not found")

@app.get("/api/v1/areas/{area_id}/workflows")
async def get_area_workflows(area_id: str):
    """Get available workflows for an area."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    if area_id == "oldham":
        workflow = MoveHomeWorkflow()
        return {"status": "ok", "workflows": [workflow.to_dict()]}

    raise HTTPException(status_code=404, detail=f"Area {area_id} not found")

# ============================================================
# WORKFLOW ENDPOINTS
# ============================================================

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow definition."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    if workflow_id == "move_home":
        workflow = MoveHomeWorkflow()
        return {"status": "ok", "workflow": workflow.to_dict()}

    raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

@app.post("/api/v1/workflows/{workflow_id}/preflight")
async def workflow_preflight(workflow_id: str, context: dict):
    """Check what information we have and what's missing."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    if workflow_id != "move_home":
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    workflow = MoveHomeWorkflow()

    have = []
    missing = []

    for inp in workflow.required_inputs:
        if inp in context:
            have.append(inp)
        else:
            missing.append(inp)

    for inp in workflow.optional_inputs:
        if inp in context:
            have.append(inp)

    return {
        "status": "ok",
        "have": have,
        "missing": missing,
        "ready": len(missing) == 0,
    }

@app.post("/api/v1/workflows/{workflow_id}/prepare")
async def workflow_prepare(workflow_id: str, context: dict):
    """Prepare all forms with available information."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow
    from uk_boring.geo import resolve_postcode

    if workflow_id != "move_home":
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    workflow = MoveHomeWorkflow()

    # Resolve place
    new_address = context.get("new_address", "")
    postcode = context.get("new_postcode", "")
    place = None
    if postcode:
        place = resolve_postcode(postcode)

    # Prepare each step
    prepared_steps = []
    for step in workflow.steps:
        prepared_steps.append({
            "step_id": step.step_id,
            "name": step.name,
            "action_class": step.action_class,
            "execution_mode": step.execution_mode,
            "official_url": step.official_url,
            "status": "ready" if all(info in context for info in step.required_info) else "missing_info",
            "missing_info": [info for info in step.required_info if info not in context],
        })

    return {
        "status": "ok",
        "workflow": workflow_id,
        "place": place.to_dict() if place else None,
        "steps": prepared_steps,
    }

@app.post("/api/v1/workflows/{workflow_id}/verify")
async def workflow_verify(workflow_id: str, step_id: str, captured: dict):
    """Verify a captured confirmation against expected receipt pattern."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    # Find the step
    workflow = MoveHomeWorkflow()
    step = None
    for s in workflow.steps:
        if s.step_id == step_id:
            step = s
            break

    if not step:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")

    # Try to find a receipt pattern
    pattern_id = f"{workflow_id}.{step_id}"
    pattern = boringuk_receipts.RECEIPT_PATTERNS.get(pattern_id)

    if not pattern and step.receipt_pattern:
        # Use inline receipt pattern
        pattern = boringuk_receipts.ReceiptPattern(
            step_id=pattern_id,
            step_name=step.name,
            method=step.execution_mode,
            url=step.official_url,
            receipt_type=step.receipt_pattern.get("type", "confirmation_page"),
            fields=[
                boringuk_receipts.FieldPattern(**f) for f in step.receipt_pattern.get("fields", [])
            ],
        )

    if not pattern:
        return {"status": "no_pattern", "message": "No receipt pattern defined for this step"}

    result = boringuk_receipts.verify_receipt(pattern, captured)

    return {
        "status": "ok",
        "step_id": step_id,
        "verification": {
            "result": result.result.value,
            "confidence": result.confidence,
            "matched_fields": result.matched_fields,
            "failed_fields": result.failed_fields,
            "failure_action": result.failure_action,
            "receipt_data": result.receipt_data,
        },
    }

# ============================================================
# HEALTH
# ============================================================

@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "service": "uk-boring-api",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    }
