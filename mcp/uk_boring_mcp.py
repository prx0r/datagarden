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
    {
        "name": "achieve_goal",
        "description": "Start working toward a goal. Returns the workflow chain needed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal_id": {"type": "string", "description": "Goal to achieve (e.g. 'move_home', 'find_local_work', 'sell_item')"},
                "context": {"type": "object", "description": "Information we already have"}
            },
            "required": ["goal_id"]
        }
    },
    {
        "name": "list_goals",
        "description": "List all available goals for a place or category.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "outlet": {"type": "string", "description": "Filter: ukboring, ukopportunity, ukproducts"},
                "place_id": {"type": "string", "description": "Filter by place"}
            }
        }
    },
    {
        "name": "get_opportunities",
        "description": "What opportunities exist in this area? (jobs, contracts, grants, business gaps)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "place_id": {"type": "string", "description": "Area to search"},
                "type": {"type": "string", "description": "Filter: job, contract, grant, business_gap"}
            },
            "required": ["place_id"]
        }
    },
    {
        "name": "earn",
        "description": "Find economic opportunities based on what a person can do. Returns grounded actions with estimated value, confidence, and route to action.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Where the person is (e.g. 'Oldham')"},
                "skills": {"type": "array", "items": {"type": "string"}, "description": "Skills (e.g. ['electrician', 'van'])"},
                "certifications": {"type": "array", "items": {"type": "string"}, "description": "Certifications (e.g. ['NICEIC'])"},
                "available_days": {"type": "array", "items": {"type": "string"}, "description": "Days available"},
                "capital": {"type": "number", "description": "Available capital in GBP"},
                "target_amount": {"type": "number", "description": "How much to make"},
                "deadline": {"type": "string", "description": "When needed by"}
            },
            "required": ["location", "skills"]
        }
    },
    {
        "name": "list_painful_tasks",
        "description": "List the most annoying UK government tasks by complaint volume. Returns DVLA, council tax, parking, used car, energy disputes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter: driving, council, parking, consumer, energy"}
            }
        }
    },
    {
        "name": "get_painful_task",
        "description": "Get detailed workflow for a specific painful task (steps, receipt pattern, failure modes).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID (e.g. 'dvla.renew_licence', 'parking.pcn_appeal')"}
            },
            "required": ["task_id"]
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


def earn(location: str, skills: list, certifications: list = None,
         available_days: list = None, capital: float = 0,
         target_amount: float = 0, deadline: str = "") -> dict:
    """Find economic opportunities based on what a person can do."""
    from uk_boring.earn import find_earn_opportunities, CapabilityEnvelope
    
    profile = CapabilityEnvelope(
        location=location,
        skills=skills,
        certifications=certifications or [],
        equipment=[],
        available_hours=8,
        available_days=available_days or [],
        capital=capital,
        vehicle='',
        radius_miles=20,
    )
    
    opps = find_earn_opportunities(profile)
    
    results = []
    for o in opps[:10]:
        results.append({
            'action': o.action,
            'title': o.title,
            'description': o.description[:200],
            'estimated_value_gbp': o.estimated_value_gbp,
            'confidence': round(o.confidence, 2),
            'distance_miles': o.distance_miles,
            'deadline': o.deadline,
            'route_to_action': o.route_to_action,
            'source': o.source,
        })
    
    return {
        "status": "ok",
        "location": location,
        "skills": skills,
        "opportunities": results,
        "count": len(results),
    }


def list_painful_tasks(category: str = None) -> dict:
    from uk_boring.workflows.painful_tasks import PAINFUL_TASKS, list_painful_tasks as lpt
    tasks = lpt(category)
    return {
        "status": "ok",
        "count": len(tasks),
        "tasks": [{
            "task_id": k,
            "name": v.name,
            "volume": v.volume,
            "category": v.category,
            "url": v.url,
            "cost": v.cost,
            "timeline": v.timeline,
        } for k, v in PAINFUL_TASKS.items() if not category or v.category == category],
    }


def get_painful_task(task_id: str) -> dict:
    from uk_boring.workflows.painful_tasks import get_painful_task as gpt
    task = gpt(task_id)
    if not task:
        return {"status": "not_found", "task_id": task_id}
    return {
        "status": "ok",
        "task_id": task_id,
        "name": task.name,
        "volume": task.volume,
        "category": task.category,
        "url": task.url,
        "cost": task.cost,
        "timeline": task.timeline,
        "steps": task.steps,
        "receipt_pattern": task.receipt_pattern,
        "failure_modes": task.failure_modes,
    }


def achieve_goal(goal_id: str, context: dict = None) -> dict:
    from uk_boring.goals import get_goal
    context = context or {}

    goal = get_goal(goal_id)
    if not goal:
        return {"status": "not_found", "message": f"Goal '{goal_id}' not found"}

    workflow_chain = []
    for wf_id in goal.workflows:
        step = {
            "workflow_id": wf_id,
            "depends_on": [],
        }
        if wf_id == "move_home":
            step["description"] = "Notify all government bodies of address change"
            step["execution_modes"] = ["api", "auth_browser", "handoff"]
        elif wf_id == "letter_workflow":
            step["description"] = "Parse letter, identify obligation, take action"
            step["execution_modes"] = ["auth_browser", "user_handoff"]
        elif wf_id == "find_provider":
            step["description"] = "Search local providers for the service needed"
            step["execution_modes"] = ["api"]
        elif wf_id == "book_service":
            step["description"] = "Book with selected provider"
            step["execution_modes"] = ["api", "auth_browser", "handoff"]
        elif wf_id == "search_contracts":
            step["description"] = "Search Contracts Finder and local tenders"
            step["execution_modes"] = ["api"]
        elif wf_id == "match_capabilities":
            step["description"] = "Match business capabilities to requirements"
            step["execution_modes"] = ["api"]
        elif wf_id == "monitor_changes":
            step["description"] = "Check planning, licensing, and business changes"
            step["execution_modes"] = ["api"]
        elif wf_id == "value_item":
            step["description"] = "Determine fair market value"
            step["execution_modes"] = ["api"]
        elif wf_id == "list_item":
            step["description"] = "List on optimal sales platform"
            step["execution_modes"] = ["api", "auth_browser"]
        elif wf_id == "find_source":
            step["description"] = "Find sources for the item"
            step["execution_modes"] = ["api"]
        elif wf_id == "verify_condition":
            step["description"] = "Verify item condition and fairness"
            step["execution_modes"] = ["api", "user_handoff"]
        else:
            step["description"] = f"Workflow: {wf_id}"
            step["execution_modes"] = ["unknown"]
        workflow_chain.append(step)

    return {
        "status": "ok",
        "goal": {
            "goal_id": goal.goal_id,
            "name": goal.name,
            "description": goal.description,
            "category": goal.category,
            "typical_duration": goal.typical_duration,
        },
        "workflow_chain": workflow_chain,
        "expected_outcomes": goal.expected_outcomes,
        "context_provided": list(context.keys()),
    }


def list_goals(outlet: str = None, place_id: str = None) -> dict:
    from uk_boring.goals import list_goals as lg
    goals = lg(outlet)
    return {
        "status": "ok",
        "count": len(goals),
        "goals": [
            {
                "goal_id": g.goal_id,
                "name": g.name,
                "description": g.description,
                "category": g.category,
                "typical_duration": g.typical_duration,
            }
            for g in goals
        ],
    }


def get_opportunities(place_id: str, type: str = None) -> dict:
    return {
        "status": "ok",
        "place_id": place_id,
        "opportunities": [],
        "note": "Opportunity scanning not yet wired to live data feeds. Use process_planning_signal / process_contract_signal to feed signals.",
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
    "earn": earn,
    "list_painful_tasks": list_painful_tasks,
    "get_painful_task": get_painful_task,
    "achieve_goal": achieve_goal,
    "list_goals": list_goals,
    "get_opportunities": get_opportunities,
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
