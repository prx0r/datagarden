#!/usr/bin/env python3
"""
UK Boring MCP Server — Regional intelligence + workflow execution.

Tools:
- resolve_place: Turn postcode into Place with all jurisdictions
- get_area_services: What services does this area have?
- get_area_workflows: What workflows can I do here?
- move_home: Start the move-home workflow
- check_mots: Check MOT history for a vehicle
- check_vehicle_tax: Check vehicle tax status
- check_council_tax: Check council tax band
- check_company: Look up a company on Companies House
- preflight: What info do I need for a workflow?
- verify_receipt: Verify a captured confirmation
- what_changed: What workflows changed recently in this area?

Usage:
    python uk_boring_mcp.py resolve_place '{"postcode": "OL1 1AA"}'
    python uk_boring_mcp.py --serve  # MCP stdio
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

TOOLS = [
    {
        "name": "resolve_place",
        "description": "Turn a UK postcode into a Place with all jurisdictional overlays: council, police, NHS, water, constituency, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode (e.g. 'OL1 1AA', 'M1 1AE', 'LS1 1BA')"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "get_area_services",
        "description": "What government services are available in this area?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "area_id": {"type": "string", "description": "Area ID (e.g. 'oldham', 'manchester', 'leeds')"}
            },
            "required": ["area_id"]
        }
    },
    {
        "name": "get_area_workflows",
        "description": "What workflows can I do in this area?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "area_id": {"type": "string", "description": "Area ID"}
            },
            "required": ["area_id"]
        }
    },
    {
        "name": "move_home",
        "description": "Start the move-home workflow. Returns all steps, what info is needed, and which steps are national vs local.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "new_postcode": {"type": "string", "description": "Postcode of new address"},
                "new_address": {"type": "string", "description": "Full new address"}
            },
            "required": ["new_postcode"]
        }
    },
    {
        "name": "check_mot",
        "description": "Check MOT history for a vehicle. Returns pass/fail, expiry, advisories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string", "description": "Vehicle registration number"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "check_vehicle_tax",
        "description": "Check if vehicle tax is current.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string", "description": "Vehicle registration number"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "check_council_tax",
        "description": "Check council tax band for an address.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "check_company",
        "description": "Look up a company on Companies House.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_number": {"type": "string", "description": "Companies House number"}
            },
            "required": ["company_number"]
        }
    },
    {
        "name": "preflight",
        "description": "Check what information we have and what's missing for a workflow.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "Workflow to check (e.g. 'move_home')"},
                "context": {"type": "object", "description": "Information we already have"}
            },
            "required": ["workflow_id", "context"]
        }
    },
    {
        "name": "verify_receipt",
        "description": "Verify a captured confirmation against expected receipt pattern.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "step_id": {"type": "string", "description": "Step to verify (e.g. 'dvla_address')"},
                "captured": {"type": "object", "description": "What was captured from the confirmation"}
            },
            "required": ["step_id", "captured"]
        }
    },
    {
        "name": "list_national_workflows",
        "description": "List all national workflows available everywhere in the UK.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter by category: address_change, vehicle, voting, business"}
            }
        }
    },
]


def resolve_place(postcode: str) -> dict:
    from uk_boring.geo import resolve_postcode
    place = resolve_postcode(postcode)
    if place:
        return {
            "status": "ok",
            "place": place.to_dict(),
            "services": ["council_tax", "waste", "parking", "planning", "electoral"],
            "national_workflows": ["dvla.address_change", "electoral.register", "hmrc.address_change", "vehicle_tax.address_change"],
            "local_workflows": ["council_tax.move_home", "waste.missed_bin", "parking.permit"],
        }
    return {"status": "not_found", "message": f"Could not resolve postcode: {postcode}"}


def get_area_services(area_id: str) -> dict:
    from uk_boring.oldham import OLDHAM_SERVICES
    if area_id == "oldham":
        return {"status": "ok", "area": area_id, "services": OLDHAM_SERVICES}
    return {"status": "not_found", "message": f"Area {area_id} not found"}


def get_area_workflows(area_id: str) -> dict:
    from uk_boring.workflows.move_home import MoveHomeWorkflow
    from uk_boring.national import list_national_workflows
    
    if area_id == "oldham":
        local = [
            {"id": "oldham.council_tax.move_home", "name": "Notify council tax of move"},
            {"id": "oldham.waste.missed_bin", "name": "Report missed bin"},
            {"id": "oldham.parking.permit", "name": "Apply for parking permit"},
        ]
    else:
        local = []
    
    return {
        "status": "ok",
        "area": area_id,
        "national": [{"id": w.workflow_id, "name": w.name} for w in list_national_workflows()],
        "local": local,
    }


def move_home(new_postcode: str, new_address: str = "") -> dict:
    from uk_boring.workflows.move_home import MoveHomeWorkflow
    from uk_boring.geo import resolve_postcode
    
    wf = MoveHomeWorkflow()
    place = resolve_postcode(new_postcode)
    
    steps = []
    for s in wf.steps:
        steps.append({
            "step_id": s.step_id,
            "name": s.name,
            "action_class": s.action_class,
            "execution_mode": s.execution_mode,
            "official_url": s.official_url,
            "status": "ready" if s.action_class == "AUTO" else "awaiting_action",
        })
    
    return {
        "status": "ok",
        "workflow": "move_home",
        "place": place.to_dict() if place else {"postcode": new_postcode},
        "steps": steps,
        "total_steps": len(steps),
        "national_steps": len([s for s in wf.steps if "national" in (s.official_url or "")]),
        "local_steps": len([s for s in wf.steps if "oldham.gov.uk" in (s.official_url or "")]),
    }


def check_mot(registration: str) -> dict:
    return {
        "status": "ready",
        "registration": registration,
        "url": f"https://www.gov.uk/check-mot-history",
        "instructions": f"Navigate to {url}, enter {registration}, capture results",
        "receipt_pattern": {
            "fields": [
                {"name": "make", "exists": True},
                {"name": "model", "exists": True},
                {"name": "mot_expiry", "pattern": "\\d{2}/\\d{2}/\\d{4}"},
            ]
        },
    }


def check_vehicle_tax(registration: str) -> dict:
    return {
        "status": "ready",
        "registration": registration,
        "url": "https://www.gov.uk/check-vehicle-tax",
        "instructions": f"Navigate to URL, enter {registration}, capture results",
    }


def check_council_tax(postcode: str) -> dict:
    return {
        "status": "ready",
        "postcode": postcode,
        "url": "https://www.gov.uk/council-tax-bands",
        "instructions": f"Navigate to URL, enter {postcode}, capture band and council",
    }


def check_company(company_number: str) -> dict:
    import requests
    try:
        resp = requests.get(
            f"https://api.company-information.service.gov.uk/company/{company_number}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "ok",
                "company_number": company_number,
                "name": data.get("company_name", ""),
                "status": data.get("status", ""),
                "incorporation_date": data.get("incorporation_date", ""),
                "sic_codes": data.get("sic_codes", []),
            }
    except Exception:
        pass
    return {"status": "unavailable", "message": "Companies House API requires key"}


def preflight(workflow_id: str, context: dict) -> dict:
    from uk_boring.workflows.move_home import MoveHomeWorkflow
    
    if workflow_id == "move_home":
        wf = MoveHomeWorkflow()
        have = [k for k in context if context[k]]
        missing = [i for i in wf.required_inputs if i not in context]
        return {"status": "ok", "have": have, "missing": missing, "ready": len(missing) == 0}
    
    return {"status": "unknown_workflow", "message": f"Workflow {workflow_id} not found"}


def verify_receipt(step_id: str, captured: dict) -> dict:
    from boringuk_receipts import verify_receipt as vr, RECEIPT_PATTERNS
    from uk_boring.workflows.move_home import MoveHomeWorkflow
    
    wf = MoveHomeWorkflow()
    step = None
    for s in wf.steps:
        if s.step_id == step_id:
            step = s
            break
    
    if not step:
        return {"status": "step_not_found", "message": f"Step {step_id} not in move_home workflow"}
    
    pattern = None
    for pid, p in RECEIPT_PATTERNS.items():
        if step_id in pid:
            pattern = p
            break
    
    if not pattern:
        return {"status": "no_pattern", "message": f"No receipt pattern for {step_id}"}
    
    result = vr(pattern, captured)
    return {
        "status": "ok",
        "step_id": step_id,
        "result": result.result.value,
        "confidence": result.confidence,
        "matched": result.matched_fields,
        "failed": result.failed_fields,
    }


def list_national_workflows(category: str = None) -> dict:
    from uk_boring.national import list_national_workflows as lnw
    workflows = lnw(category)
    return {
        "status": "ok",
        "count": len(workflows),
        "workflows": [{"id": w.workflow_id, "name": w.name, "category": w.category, "url": w.url} for w in workflows],
    }


DISPATCH = {
    "resolve_place": resolve_place,
    "get_area_services": get_area_services,
    "get_area_workflows": get_area_workflows,
    "move_home": move_home,
    "check_mot": check_mot,
    "check_vehicle_tax": check_vehicle_tax,
    "check_council_tax": check_council_tax,
    "check_company": check_company,
    "preflight": preflight,
    "verify_receipt": verify_receipt,
    "list_national_workflows": list_national_workflows,
}


def handle_tool_call(name: str, args: dict) -> dict:
    func = DISPATCH.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except TypeError as e:
        return {"error": f"Invalid args: {e}"}


def run_mcp_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        msg_id = msg.get("id")
        if method == "initialize":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "uk-boring", "version": "0.1.0", "description": "UK Boring — Get boring British things done. Regional intelligence + workflow execution."}}}
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = msg.get("params", {})
            result = handle_tool_call(params.get("name", ""), params.get("arguments", {}))
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}}
        else:
            response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
        print(json.dumps(response), flush=True)


if __name__ == '__main__':
    if '--serve' in sys.argv:
        run_mcp_stdio()
    elif len(sys.argv) > 2:
        result = handle_tool_call(sys.argv[1], json.loads(sys.argv[2]))
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps({"name": "uk-boring", "tools": [t["name"] for t in TOOLS]}, indent=2))
