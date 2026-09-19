#!/usr/bin/env python3
"""
UK Admin MCP Server - Get boring British things done.

PR5 Truth Contract: Every response includes source verification metadata.
Every workflow step states its verification status against live GOV.UK pages.
Boring UK's value IS verification. Don't fake it.

Tools (original):
- explain_task, check_requirements, can_agent_do_it
- moving_house_checklist, start_sole_trader, tax_obligations
- new_parent_admin, used_car_checks, lost_passport
- manage_mot, support_check, company_setup

Tools (Boring UK Workflows - 12 new):
- move_house, manage_car, onboard_car
- start_sole_trader, manage_business, change_details_everywhere
- renew_passport, start_driving, start_regulated_business
- resolve_letter, admin_audit, renewals

Tools (Verification):
- verification_status

Usage:
    python uk_admin_mcp.py                     # List tools
    python uk_admin_mcp.py <tool> '<json>'     # Call tool
    python uk_admin_mcp.py --serve             # MCP stdio server
"""

import json
import hashlib
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'uk_admin' / 'data'
TASKS_DIR = DATA_DIR / 'tasks'
sys.path.insert(0, str(ROOT))


# ============================================================
# TRUTH CONTRACT - PR5
# ============================================================

TRUTH_CLASSES = {
    "VERIFIED": "Source checked against live page. Hash matches.",
    "DERIVED": "Inferred from verified sources. Not directly checked.",
    "ESTIMATED": "Best guess based on related data. May be outdated.",
    "CONCEPTUAL": "Source URL provided but page content not checked.",
}

VERIFICATION_METHODS = {
    "manual_check": "Human or agent fetched and verified the page content",
    "api_check": "Verified via official API endpoint",
    "automated": "Automated hash verification against known good",
    "none": "No verification performed",
}

DEFAULT_AS_OF = "2026-09-19T00:00:00Z"
VERIFICATION_PERIOD_DAYS = 30


def _now_iso():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _default_next_verification():
    return (datetime.utcnow() + timedelta(days=VERIFICATION_PERIOD_DAYS)).strftime('%Y-%m-%dT00:00:00Z')


def _make_source_hash(url):
    """Placeholder hash for source URL content. In production, fetch and hash the page."""
    return f"sha256:{hashlib.sha256(url.encode()).hexdigest()[:16]}"


def _truth_wrap(tool_id, result, truth_class="CONCEPTUAL", confidence=0.0,
                evidence=None, method_id="unknown", method_version="0.1.0",
                limitations=None):
    """Wrap any tool result in the PR5 truth contract."""
    return {
        "capability": f"uk_admin.{tool_id}",
        "as_of": DEFAULT_AS_OF,
        "result": result,
        "truth_class": truth_class,
        "confidence": confidence,
        "evidence": evidence or [],
        "method": {"id": method_id, "version": method_version},
        "limitations": limitations or ["Steps not yet verified against live GOV.UK pages"],
        "action": {"class": "USER_HANDOFF"},
    }


def _step_with_verification(step_num, task, action_class, source_url,
                             verification_method="none", verified_at=None,
                             source_hash=None, **extra):
    """Build a workflow step with full PR5 verification metadata."""
    if source_hash is None:
        source_hash = _make_source_hash(source_url) if source_url else None
    if verified_at is None:
        verified_at = DEFAULT_AS_OF if verification_method != "none" else None

    next_due = None
    if verified_at:
        try:
            dt = datetime.fromisoformat(verified_at.replace('Z', '+00:00'))
            next_due = (dt + timedelta(days=VERIFICATION_PERIOD_DAYS)).strftime('%Y-%m-%dT00:00:00Z')
        except (ValueError, TypeError):
            next_due = _default_next_verification()

    verification_status = (
        "VERIFIED" if verification_method not in ("none",) and verified_at
        else "NOT_VERIFIED — source_url provided but not checked"
    )

    step = {
        "step": step_num,
        "task": task,
        "action_class": action_class,
        "source_url": source_url,
        "source_hash": source_hash,
        "verified_at": verified_at,
        "next_verification_due": next_due,
        "verification_method": verification_method,
        "verification_status": verification_status,
    }
    step.update(extra)
    return step


# ============================================================
# ACTION CLASSIFICATION
# ============================================================

ACTION_CLASSES = {
    "AUTO": "Agent can execute fully without human involvement",
    "APPROVAL_REQUIRED": "Agent executes but requires explicit human approval",
    "USER_HANDOFF": "Must be completed by the user directly",
    "UNSUPPORTED": "Cannot be handled by agent currently",
}


# ============================================================
# CAPABILITY FILTER LEVELS
# ============================================================

CAPABILITY_LEVELS = {
    0: "ANSWER - just information, ChatGPT handles this",
    1: "EXPLAIN - walkthrough, mostly no build needed",
    2: "PREPARE - gather requirements, maybe build",
    3: "EXECUTE - actually do it, build yes",
    4: "MAINTAIN - ongoing compliance, very yes",
    5: "ORCHESTRATE - full lifecycle management, best category",
}


# ============================================================
# STATE STORE (persistent JSON files in DATA_DIR)
# ============================================================

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_state(filename):
    _ensure_data_dir()
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_state(filename, state):
    _ensure_data_dir()
    path = DATA_DIR / filename
    with open(path, 'w') as f:
        json.dump(state, f, indent=2, default=str)


# ============================================================
# CURATED TASK DATABASE (with PR5 verification metadata)
# ============================================================

def _task_row(tid, row):
    """Inject verification metadata into a task loaded from JSONL."""
    row.setdefault('task_id', tid)
    row.setdefault('verified_at', None)
    row.setdefault('source_url', row.get('official_source', row.get('url', '')))
    row.setdefault('source_hash', _make_source_hash(row.get('source_url', '')) if row.get('source_url') else None)
    row.setdefault('verification_method', 'none')
    row.setdefault('truth_class', 'CONCEPTUAL')
    row.setdefault('next_verification_due', None)
    return row


def _load_tasks():
    """Load curated tasks from the JSONL file and inject verification metadata."""
    tasks = {}
    jsonl_path = TASKS_DIR / 'uk_admin_tasks_2026-09-19.jsonl'
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    tid = row.get('task_id', '')
                    tasks[tid] = _task_row(tid, row)
                except json.JSONDecodeError:
                    continue
    return tasks


TASK_DB = _load_tasks()


# ============================================================
# TOOLS (original 12)
# ============================================================

TOOLS = [
    {
        "name": "explain_task",
        "description": "How do I do X? Full walkthrough for a UK government task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to explain"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "check_requirements",
        "description": "What do I need for X? Prerequisites checklist.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to check"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "can_agent_do_it",
        "description": "Can the agent handle this? Permission check.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to check"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "moving_house_checklist",
        "description": "I've moved house, what do I update?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "new_address": {"type": "string"},
                "move_date": {"type": "string"}
            },
            "required": ["new_address", "move_date"]
        }
    },
    {
        "name": "start_sole_trader",
        "description": "Set me up as a sole trader.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "business_name": {"type": "string"},
                "business_type": {"type": "string"}
            }
        }
    },
    {
        "name": "tax_obligations",
        "description": "What do I need to file this year?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {"type": "string"}
            },
            "required": ["situation"]
        }
    },
    {
        "name": "new_parent_admin",
        "description": "I'm having a baby, what government things?",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "used_car_checks",
        "description": "I'm buying a used car, check everything.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string"},
                "make": {"type": "string"},
                "model": {"type": "string"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "lost_passport",
        "description": "I lost my passport, what do I do?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "was_stolen": {"type": "boolean"}
            }
        }
    },
    {
        "name": "manage_mot",
        "description": "When does my MOT run out?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "support_check",
        "description": "What benefits might I qualify for?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {"type": "string"}
            },
            "required": ["situation"]
        }
    },
    {
        "name": "company_setup",
        "description": "Set up a limited company.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "sector": {"type": "string"}
            }
        }
    },
    # ---- BORING UK WORKFLOW TOOLS (12 new) ----
    {
        "name": "move_house",
        "description": "Full moving house checklist with dependencies and timing. Covers DVLA, council tax, electoral roll, utilities, insurance, banks, Royal Mail redirection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "move_date": {"type": "string", "description": "Date you move (YYYY-MM-DD)"},
                "new_address": {"type": "string", "description": "Your new address"},
                "old_address": {"type": "string", "description": "Your old address (optional)"}
            },
            "required": ["move_date", "new_address"]
        }
    },
    {
        "name": "manage_car",
        "description": "MOT, tax, V5C, renewals, recalls - persistent car state tracking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string", "description": "Vehicle registration number"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "onboard_car",
        "description": "Just bought a used car, do everything needed: checks, V5C transfer, insurance, tax.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "registration": {"type": "string", "description": "Vehicle registration number"}
            },
            "required": ["registration"]
        }
    },
    {
        "name": "manage_business",
        "description": "Keep a company compliant: deadlines, filings, Corporation Tax, Confirmation Statement.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_number": {"type": "string", "description": "Companies House company number"}
            },
            "required": ["company_number"]
        }
    },
    {
        "name": "change_details_everywhere",
        "description": "Fix name or address everywhere: DVLA, HMRC, passport, banks, electoral, NHS, insurance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detail_type": {"type": "string", "description": "What changed: 'name' or 'address'"},
                "old_value": {"type": "string", "description": "Your old name or address"},
                "new_value": {"type": "string", "description": "Your new name or address"}
            },
            "required": ["detail_type", "old_value", "new_value"]
        }
    },
    {
        "name": "renew_passport",
        "description": "Passport renewal workflow with all steps, fees, and timing.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "start_driving",
        "description": "Provisional to full driving licence workflow: theory test, practical test, fees.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "start_regulated_business",
        "description": "Food business, licensed premises, taxi, construction - regulatory registration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "business_type": {"type": "string", "description": "Type: 'food', 'premises', 'taxi', 'construction'"}
            },
            "required": ["business_type"]
        }
    },
    {
        "name": "resolve_letter",
        "description": "Parse a government letter, identify the task, and build a workflow to handle it.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "letter_text": {"type": "string", "description": "Text content of the government letter"}
            },
            "required": ["letter_text"]
        }
    },
    {
        "name": "admin_audit",
        "description": "What boring stuff are you forgetting? Audit passport, MOT, tax, company filings, insurance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_state": {
                    "type": "object",
                    "description": "Your current admin state: passport_expiry, driving_licence_expiry, vehicles, company_number, insurance_renewals, self_assessment_last_filed"
                }
            },
            "required": ["current_state"]
        }
    },
    {
        "name": "renewals",
        "description": "Everything expiring in the next N days: MOT, tax, insurance, passport, company filings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "How many days ahead to check (default 30)"}
            }
        }
    },
    # ---- VERIFICATION TOOL ----
    {
        "name": "verification_status",
        "description": "Show verification status of all tasks and workflow steps. Which are verified, which are conceptual.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_filter": {"type": "string", "description": "Filter to specific task ID (optional)"}
            }
        }
    },
]


# ============================================================
# HELPERS
# ============================================================

def _find_task(query):
    q = query.lower().strip()
    if q in TASK_DB:
        return TASK_DB[q]
    for tid, task in TASK_DB.items():
        if q.replace(' ', '_') == tid:
            return task
    for tid, task in TASK_DB.items():
        if q in task.get('task_name', '').lower():
            return task
    keywords = q.split()
    for tid, task in TASK_DB.items():
        words = task.get('task_name', '').lower().split()
        if any(kw in words for kw in keywords):
            return task
    return None


# ============================================================
# IMPLEMENTATIONS (original 12) - with PR5 truth contract
# ============================================================

def explain_task(task):
    td = _find_task(task)
    if not td:
        available = {}
        for tid, t in TASK_DB.items():
            available.setdefault(t.get('category', 'unknown'), []).append(tid)
        result = {'status': 'not_found', 'query': task, 'available_tasks': available}
        return _truth_wrap('explain_task', result, truth_class="VERIFIED",
                          confidence=1.0, evidence=[],
                          limitations=["Task not found in database"])

    tc = td.get('truth_class', 'CONCEPTUAL')
    ev = []
    if td.get('source_url'):
        ev.append({"type": "source_url", "url": td['source_url'], "hash": td.get('source_hash')})

    result = {
        'status': 'ok',
        'task': td.get('task_name', task),
        'category': td.get('category', ''),
        'authority': td.get('authority', ''),
        'url': td.get('url', ''),
        'cost': f"\u00a3{td['cost_gbp']:.2f}" if td.get('cost_gbp') else 'Free',
        'time': td.get('takes_time', 'Unknown'),
        'steps': td.get('how_to', []),
        'related_tasks': td.get('related_tasks', []),
        'recurring': td.get('is_recurring', False),
        'recurrence': td.get('recurrence', ''),
        'verification': {
            'truth_class': tc,
            'verified_at': td.get('verified_at'),
            'verification_method': td.get('verification_method', 'none'),
            'source_url': td.get('source_url', ''),
            'source_hash': td.get('source_hash'),
        },
    }
    conf = 0.9 if tc == "VERIFIED" else 0.5 if tc == "DERIVED" else 0.2 if tc == "ESTIMATED" else 0.1
    return _truth_wrap('explain_task', result, truth_class=tc, confidence=conf,
                      evidence=ev, limitations=[] if tc == "VERIFIED" else
                      ["Source page not verified against live GOV.UK content"])


def check_requirements(task):
    td = _find_task(task)
    if not td:
        result = {'status': 'not_found', 'query': task}
        return _truth_wrap('check_requirements', result, truth_class="VERIFIED",
                          confidence=1.0, limitations=["Task not found"])

    reqs = td.get('requires', [])
    details = {
        'identity': 'Valid photo ID (passport, driving licence, or biometric residence permit)',
        'address': 'Your current address (proof may be needed)',
        'new_address': 'Your new address',
        'old_address': 'Your previous address',
        'move_date': 'Date you moved',
        'photos': 'Digital passport photo (white background, taken within last month)',
        'photo': 'Digital passport photo',
        'driving_licence_number': 'Your driving licence number',
        'national_insurance_number': 'Your NI number (found on payslip, P60, or letter from HMRC)',
        'vehicle_registration': 'Vehicle registration number (e.g. AB12 CDE)',
        'licence_details': 'Your current driving licence details',
        'insurance': 'Valid vehicle insurance',
        'mot_certificate': 'Valid MOT certificate',
        'existing_passport': 'Your current/previous passport',
        'birth_certificate': 'Your birth certificate',
        'lost_or_stolen_declaration': 'Lost or stolen declaration form',
        'passport_number': 'Your passport number',
        'personal_details': 'Full name, date of birth, address',
        'countersignatory': 'Someone who can countersign (known you 2+ years, not related)',
        'employment_history': 'Your employment history',
        'income_details': 'Income details (payslips, P60, bank statements)',
        'expenses': 'Expense receipts',
        'tax_reference': 'Your UTR or tax reference number',
        'payment_method': 'Payment method (card, bank transfer, direct debit)',
        'p60': 'Your P60 end-of-year tax summary',
        'p45': 'Your P45 if you left a job',
        'bank_details': 'Bank account details for payments/refunds',
        'baby_details': "Baby's full name, date of birth, place of birth",
        'parents_details': "Parents' names, occupations, addresses",
        'baby_birth_certificate': "Baby's birth certificate",
        'housing_costs': 'Housing costs (rent, mortgage)',
        'health_conditions': 'Health conditions and how they affect you',
        'care_needs': 'Care and mobility needs',
        'company_number': 'Company registration number from Companies House',
        'company_name': 'Registered company name',
        'accounts': 'Company financial accounts',
        'tax_computation': 'Corporation tax computation',
        'turnover_data': 'VAT turnover and sales/purchase figures',
        'vat_number': 'Your VAT registration number',
        'business_details': 'Business name, type, start date',
        'new_keeper_details': "New keeper's name and address",
        'v5c': 'V5C vehicle registration certificate',
    }
    checklist = [{'requirement': r, 'details': details.get(r, 'Check GOV.UK for specifics')} for r in reqs]
    tc = td.get('truth_class', 'CONCEPTUAL')
    result = {
        'status': 'ok',
        'task': td.get('task_name', task),
        'url': td.get('url', ''),
        'requirements': checklist,
        'count': len(reqs),
        'verification': {
            'truth_class': tc,
            'verified_at': td.get('verified_at'),
            'source_url': td.get('source_url', ''),
        },
    }
    conf = 0.8 if tc == "VERIFIED" else 0.5 if tc == "DERIVED" else 0.2
    return _truth_wrap('check_requirements', result, truth_class=tc, confidence=conf,
                      evidence=[{"type": "source_url", "url": td.get('source_url', '')}],
                      limitations=[] if tc == "VERIFIED" else
                      ["Requirements sourced from curated data, not verified against live page"])


def can_agent_do_it(task):
    td = _find_task(task)
    if not td:
        result = {'status': 'not_found', 'query': task}
        return _truth_wrap('can_agent_do_it', result, truth_class="VERIFIED",
                          confidence=1.0, limitations=["Task not found"])

    perms = td.get('agent_permissions', {})
    what_agent_can = []
    what_user_must = []
    if perms.get('explain'):
        what_agent_can.append('Explain the process step-by-step')
    if perms.get('gather_requirements'):
        what_agent_can.append('Gather and list all requirements')
    if perms.get('prefill'):
        what_agent_can.append('Pre-fill forms with your details')
    if perms.get('submit'):
        what_agent_can.append('Submit the application on your behalf')
    else:
        what_user_must.append('You must submit the form yourself')
    payment = perms.get('payment', 'not_possible')
    if payment == 'explicit_approval':
        what_user_must.append('You must approve any payment')
    elif payment == 'not_possible':
        what_user_must.append('Payment must be made by you directly')

    tc = td.get('truth_class', 'CONCEPTUAL')
    result = {
        'status': 'ok',
        'task': td.get('task_name', task),
        'agent_can_do': what_agent_can,
        'user_must_do': what_user_must,
        'permissions': perms,
        'verdict': 'FULLY_ASSISTED' if perms.get('submit') and payment != 'not_possible' else 'ASSISTED_WITH_APPROVAL' if perms.get('prefill') else 'GUIDANCE_ONLY',
        'verification': {
            'truth_class': tc,
            'verified_at': td.get('verified_at'),
            'source_url': td.get('source_url', ''),
        },
    }
    return _truth_wrap('can_agent_do_it', result, truth_class=tc,
                      confidence=0.5 if tc == "CONCEPTUAL" else 0.8,
                      evidence=[{"type": "source_url", "url": td.get('source_url', '')}])


def moving_house_checklist(new_address, move_date, old_address=''):
    items = [
        {'task': 'update_address', 'what': 'Update driving licence address', 'authority': 'DVLA', 'cost': 'Free', 'deadline': 'Within 8 weeks', 'source_url': 'https://www.gov.uk/change-address-driving-licence'},
        {'task': 'update_vehicle_tax', 'what': 'Update vehicle tax address', 'authority': 'DVLA', 'cost': 'Free', 'deadline': 'Immediately', 'source_url': 'https://www.gov.uk/vehicle-tax'},
        {'task': 'update_council_tax', 'what': 'Notify council for council tax', 'authority': 'Local Council', 'cost': 'Free', 'deadline': 'On or before move date', 'source_url': 'https://www.gov.uk/council-tax'},
        {'task': 'update_electoral_roll', 'what': 'Register to vote at new address', 'authority': 'Electoral Commission', 'cost': 'Free', 'deadline': '12 working days before election', 'source_url': 'https://www.gov.uk/register-to-vote'},
        {'task': 'redirect_post', 'what': 'Redirect your post', 'authority': 'Royal Mail', 'cost': 'From 82.99', 'deadline': 'Before you move', 'source_url': 'https://www.royalmail.com/redirection'},
        {'task': 'update_banks', 'what': 'Update bank and credit card addresses', 'authority': 'Banks', 'cost': 'Free', 'deadline': 'Within a few weeks', 'source_url': ''},
        {'task': 'update_utilities', 'what': 'Notify gas, electric, water, council', 'authority': 'Utility providers', 'cost': 'Free', 'deadline': 'Before you move', 'source_url': ''},
        {'task': 'update_insurance', 'what': 'Update home, car, and other insurance', 'authority': 'Insurers', 'cost': 'Free', 'deadline': 'Before you move', 'source_url': ''},
    ]
    for item in items:
        item['verification'] = {
            'truth_class': 'CONCEPTUAL',
            'verification_method': 'none',
            'source_hash': _make_source_hash(item['source_url']) if item['source_url'] else None,
        }
    result = {
        'status': 'ok',
        'new_address': new_address,
        'old_address': old_address,
        'move_date': move_date,
        'checklist': items,
        'count': len(items),
        'tip': 'Start with DVLA and council tax - they have legal deadlines.',
    }
    return _truth_wrap('moving_house_checklist', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": i['source_url']} for i in items if i['source_url']],
                      limitations=["Checklist items not verified against live GOV.UK pages"])


def start_sole_trader(business_name='', business_type=''):
    td = TASK_DB.get('setup_sole_trader', {})
    tc = td.get('truth_class', 'CONCEPTUAL')
    result = {
        'status': 'ok',
        'task': 'Set up as a sole trader',
        'business_name': business_name,
        'business_type': business_type,
        'steps': td.get('how_to', []),
        'cost': 'Free',
        'time': '10 working days for UTR',
        'url': td.get('url', ''),
        'what_you_need': [
            'National Insurance number',
            'Business name and type',
            'Business start date',
            'Business address',
        ],
        'after_registering': [
            'Keep records of all income and expenses',
            'File Self Assessment tax return by 31 January',
            'Pay tax and National Insurance by 31 January and 31 July',
            'Consider registering for VAT if turnover exceeds 85,000',
        ],
        'verification': {
            'truth_class': tc,
            'verified_at': td.get('verified_at'),
            'source_url': td.get('source_url', ''),
        },
    }
    return _truth_wrap('start_sole_trader', result, truth_class=tc,
                      confidence=0.5 if tc == "CONCEPTUAL" else 0.8,
                      evidence=[{"type": "source_url", "url": td.get('source_url', '')}])


def tax_obligations(situation):
    situation_lower = situation.lower().strip()
    obligations = []
    if 'employed' in situation_lower and 'sole_trader' not in situation_lower and 'company' not in situation_lower:
        obligations = [
            {'form': 'PAYE (automatic)', 'deadline': 'Monthly', 'note': 'Your employer handles this'},
            {'form': 'P60', 'deadline': 'End of May', 'note': 'Your employer gives you this'},
        ]
    elif 'sole_trader' in situation_lower or 'self_employed' in situation_lower:
        obligations = [
            {'form': 'Self Assessment tax return', 'deadline': '31 January', 'note': 'File online via Government Gateway'},
            {'form': 'Payment on account', 'deadline': '31 July', 'note': 'If tax bill over 1,000'},
            {'form': 'VAT return', 'deadline': 'Quarterly', 'note': 'Only if registered for VAT'},
        ]
    elif 'company' in situation_lower or 'limited' in situation_lower:
        obligations = [
            {'form': 'Company Tax Return', 'deadline': '12 months after accounting period end', 'note': 'File with HMRC'},
            {'form': 'Corporation Tax payment', 'deadline': '9 months and 1 day after accounting period end', 'note': 'Pay HMRC'},
            {'form': 'Annual Confirmation Statement', 'deadline': 'Every year', 'note': 'File with Companies House'},
            {'form': 'Accounts', 'deadline': '9 months after accounting period end', 'note': 'File with Companies House'},
            {'form': 'VAT return', 'deadline': 'Quarterly', 'note': 'Only if registered for VAT'},
        ]
    elif 'landlord' in situation_lower or 'rental' in situation_lower:
        obligations = [
            {'form': 'Self Assessment tax return', 'deadline': '31 January', 'note': 'Declare rental income'},
            {'form': 'Landlord registration', 'deadline': 'Varies by council', 'note': 'Check with your local council'},
        ]
    else:
        obligations = [
            {'form': 'Check your tax account', 'deadline': 'Now', 'note': 'Log in to see what HMRC expects from you'},
        ]
    result = {
        'status': 'ok',
        'situation': situation,
        'obligations': obligations,
        'tip': 'Log in to your Personal Tax Account to see exactly what HMRC expects from you.',
        'url': 'https://www.gov.uk/log-in-register-hmrc-online-services',
    }
    return _truth_wrap('tax_obligations', result, truth_class="DERIVED",
                      confidence=0.6,
                      evidence=[{"type": "source_url", "url": "https://www.gov.uk/log-in-register-hmrc-online-services"}],
                      limitations=["Tax obligations derived from general guidance, not personalised"])


def new_parent_admin():
    result = {
        'status': 'ok',
        'checklist': [
            {'step': 'Register the birth', 'deadline': 'Within 42 days', 'cost': '11.00', 'where': 'Local register office',
             'source_url': 'https://www.gov.uk/child-birth-registration'},
            {'step': 'Apply for Child Benefit', 'deadline': 'As soon as possible', 'cost': 'Free', 'where': 'HMRC',
             'source_url': 'https://www.gov.uk/child-benefit'},
            {'step': 'Update council tax', 'deadline': 'Before the birth', 'cost': 'Free', 'where': 'Your council',
             'source_url': 'https://www.gov.uk/council-tax'},
            {'step': 'Notify your employer', 'deadline': '15 weeks before due date', 'cost': 'Free', 'where': 'Your employer',
             'source_url': ''},
            {'step': 'Check tax code', 'deadline': 'After birth', 'cost': 'Free', 'where': 'HMRC',
             'source_url': 'https://www.gov.uk/check-income-tax-returns'},
        ],
        'tip': 'Register the birth first - you need the birth certificate for everything else.',
    }
    return _truth_wrap('new_parent_admin', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": "https://www.gov.uk/child-birth-registration"}],
                      limitations=["Checklist steps not individually verified against live GOV.UK pages"])


def used_car_checks(registration, make='', model=''):
    result = {
        'status': 'ok',
        'registration': registration,
        'make': make,
        'model': model,
        'checks': [
            {'check': 'MOT history', 'what': 'Passes, failures, advisories', 'source_url': 'https://www.gov.uk/check-mot-history', 'free': True},
            {'check': 'Vehicle tax', 'what': 'Current tax status and expiry', 'source_url': 'https://www.gov.uk/check-vehicle-tax', 'free': True},
            {'check': 'Recall check', 'what': 'Outstanding safety recalls', 'source_url': 'https://www.gov.uk/check-vehicle-recalls', 'free': True},
            {'check': 'Insurance group', 'what': 'How expensive to insure', 'source_url': 'https://www.motorway.co.uk/guides/insurance-groups-explained', 'free': True},
            {'check': 'HPI check', 'what': 'Finance, written off, stolen', 'source_url': 'https://www.checkcardetails.co.uk/', 'free': False},
        ],
        'red_flags': [
            'Advisories left unrepaired',
            'Short MOT (less than 6 months)',
            'Tax about to expire',
            'Large number of previous keepers',
            "Mileage doesn't match service history",
        ],
        'tip': 'Always check MOT history and get a vehicle history check before buying.',
    }
    return _truth_wrap('used_car_checks', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": c['source_url']} for c in result['checks'] if c['source_url']],
                      limitations=["Check URLs not verified against live pages"])


def lost_passport(was_stolen=False):
    result = {
        'status': 'ok',
        'situation': 'stolen' if was_stolen else 'lost',
        'steps': [
            '1. Report it: https://www.gov.uk/report-a-lost-or-stolen-passport',
            '2. Your passport is cancelled immediately',
            '3. If stolen, report to police',
            '4. Apply for replacement: https://www.gov.uk/replace-lost-stolen-passport',
            '5. You need a new photo and may need a countersignatory',
            '6. Pay 82.50',
            '7. New passport arrives in about 10 weeks',
        ],
        'cost': '82.50',
        'time': '10 weeks',
    }
    return _truth_wrap('lost_passport', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": "https://www.gov.uk/report-a-lost-or-stolen-passport"},
                                {"type": "source_url", "url": "https://www.gov.uk/replace-lost-stolen-passport"}],
                      limitations=["Steps not verified against live GOV.UK pages"])


def manage_mot(registration):
    result = {
        'status': 'ok',
        'registration': registration,
        'url': 'https://www.gov.uk/check-mot-history',
        'steps': [
            '1. Go to https://www.gov.uk/check-mot-history',
            '2. Enter registration: ' + registration,
            '3. See MOT history, next expiry date, and advisories',
        ],
        'reminder_url': 'https://www.gov.uk/mot-reminders',
    }
    return _truth_wrap('manage_mot', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": "https://www.gov.uk/check-mot-history"}],
                      limitations=["Steps not verified against live GOV.UK page"])


def support_check(situation):
    sit = situation.lower()
    benefits = []
    if any(w in sit for w in ['kid', 'child', 'baby', 'family', 'parent']):
        benefits.append({'benefit': 'Child Benefit', 'amount': '25.60/week (eldest)', 'source_url': 'https://www.gov.uk/child-benefit'})
    if any(w in sit for w in ['unemploy', 'jobseek', 'looking for work']):
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Up to 393.45/month (under 25)', 'source_url': 'https://www.gov.uk/universal-credit'})
    if any(w in sit for w in ['disabled', 'disability', 'ill', 'mental health', 'mobility']):
        benefits.append({'benefit': 'PIP', 'amount': '72.65-184.25/week', 'source_url': 'https://www.gov.uk/pip'})
        benefits.append({'benefit': 'Employment and Support Allowance', 'amount': '84.80/week', 'source_url': 'https://www.gov.uk/employment-and-support-allowance'})
    if any(w in sit for w in ['low income', 'struggling', 'rent', 'housing']):
        benefits.append({'benefit': 'Universal Credit (housing element)', 'amount': 'Varies by area', 'source_url': 'https://www.gov.uk/universal-credit'})
        benefits.append({'benefit': 'Council Tax Reduction', 'amount': 'Up to 100%', 'source_url': 'https://www.gov.uk/council-tax-reduction'})
    if any(w in sit for w in ['carer', 'looking after']):
        benefits.append({'benefit': "Carer's Allowance", 'amount': '81.90/week', 'source_url': 'https://www.gov.uk/carers-allowance'})
    if not benefits:
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Varies', 'source_url': 'https://www.gov.uk/universal-credit'})
    result = {
        'status': 'ok',
        'situation': situation,
        'possible_benefits': benefits,
        'calculator': 'https://www.gov.uk/benefits-calculators',
    }
    return _truth_wrap('support_check', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": b['source_url']} for b in benefits if b.get('source_url')],
                      limitations=["Benefit amounts and eligibility not verified against live pages"])


def company_setup(company_name='', sector=''):
    result = {
        'status': 'ok',
        'company_name': company_name,
        'sector': sector,
        'steps': [
            '1. Choose a company name (check availability at Companies House)',
            '2. Decide on registered office address',
            '3. Appoint at least one director (can be you)',
            '4. Create articles of association (standard template available)',
            '5. Register at Companies House: https://www.gov.uk/limited-company-formation',
            '6. Cost: 12 online (or 40 by post)',
            '7. Register for Corporation Tax: https://www.gov.uk/register-for-corporation-tax',
            '8. Open a business bank account',
        ],
        'cost': '12',
        'time': '24 hours (online)',
        'after_registering': [
            'Register for Corporation Tax (HMRC)',
            'Register for VAT if turnover exceeds 85,000',
            'Set up payroll if employing staff',
            'File annual accounts with Companies House',
            'File Company Tax Return with HMRC',
        ],
        'tip': 'Use the standard articles of association to save time and money.',
    }
    return _truth_wrap('company_setup', result, truth_class="CONCEPTUAL",
                      confidence=0.3,
                      evidence=[{"type": "source_url", "url": "https://www.gov.uk/limited-company-formation"}],
                      limitations=["Steps not verified against live GOV.UK pages"])


# ============================================================
# BORING UK WORKFLOW IMPLEMENTATIONS (12 new tools) - PR5
# ============================================================

def move_house(move_date, new_address, old_address=''):
    try:
        move_dt = datetime.strptime(move_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        move_dt = None

    def _days_before(n):
        if move_dt:
            return (move_dt - timedelta(days=n)).strftime('%Y-%m-%d')
        return f'{n} days before move'

    workflow_steps = [
        _step_with_verification(1, 'Notify current council', 'USER_HANDOFF',
            'https://www.gov.uk/council-tax',
            verification_method='none',
            deadline=_days_before(14),
            authority='Old council',
            note='Council tax is a legal obligation. Contact both old and new councils.'),
        _step_with_verification(2, 'Notify new council', 'USER_HANDOFF',
            'https://www.gov.uk/find-local-council',
            verification_method='none',
            deadline=move_date,
            authority='New council',
            dependency='step_1'),
        _step_with_verification(3, 'Update driving licence', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/change-address-driving-licence',
            verification_method='none',
            deadline=_days_before(0),
            authority='DVLA',
            deadline_legal='Within 8 weeks of moving',
            dependency=None,
            fee='Free'),
        _step_with_verification(4, 'Update vehicle tax', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/vehicle-tax',
            verification_method='none',
            deadline=_days_before(0),
            authority='DVLA',
            dependency='step_3',
            fee='Free'),
        _step_with_verification(5, 'Register to vote at new address', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/register-to-vote',
            verification_method='none',
            deadline=_days_before(12),
            authority='Electoral Commission',
            dependency=None),
        _step_with_verification(6, 'Redirect post via Royal Mail', 'APPROVAL_REQUIRED',
            'https://www.royalmail.com/redirection',
            verification_method='none',
            deadline=_days_before(5),
            authority='Royal Mail',
            dependency=None,
            fee='From 82.99 for 12 months'),
        _step_with_verification(7, 'Notify banks and credit cards', 'USER_HANDOFF',
            '',
            verification_method='none',
            deadline=_days_before(-7),
            authority='Your banks',
            dependency=None,
            note='Update each bank separately.'),
        _step_with_verification(8, 'Notify utility providers', 'USER_HANDOFF',
            '',
            verification_method='none',
            deadline=_days_before(7),
            authority='Utility providers',
            dependency=None,
            note='Take meter readings on move day.'),
        _step_with_verification(9, 'Update insurance policies', 'USER_HANDOFF',
            '',
            verification_method='none',
            deadline=_days_before(0),
            authority='Insurers',
            dependency=None,
            note='Car insurance must reflect new address.'),
        _step_with_verification(10, 'Notify employer', 'USER_HANDOFF',
            '',
            verification_method='none',
            deadline=_days_before(7),
            authority='Your employer',
            dependency=None),
        _step_with_verification(11, 'Notify GP and dentist', 'USER_HANDOFF',
            '',
            verification_method='none',
            deadline=_days_before(-14),
            authority='NHS',
            dependency=None),
        _step_with_verification(12, 'Notify HMRC of address change', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/update-hmrc-your-personal-details',
            verification_method='none',
            deadline=_days_before(0),
            authority='HMRC',
            dependency=None),
    ]

    verified_count = sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED')
    total = len(workflow_steps)

    result = {
        'status': 'ok',
        'task': 'Move house - full workflow',
        'capability_level': 5,
        'workflow_steps': workflow_steps,
        'agent_actions': [s['task'] for s in workflow_steps if s['action_class'] in ('AUTO', 'APPROVAL_REQUIRED')],
        'user_actions': [s['task'] for s in workflow_steps if s['action_class'] == 'USER_HANDOFF'],
        'required_documents': ['Driving licence', 'V5C (if you own a vehicle)', 'Bank cards', 'ID for council registration'],
        'deadlines': [
            'DVLA address change: within 8 weeks of moving (legal requirement)',
            'Council tax: notify on or before move date',
            'Electoral roll: register 12 working days before an election',
        ],
        'fees': [
            'Royal Mail redirection: from 82.99 for 12 months',
            'DVLA address change: Free',
            'Council tax: varies by band',
        ],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Forgetting DVLA update (fine up to 1,000)',
            'Not updating car insurance (policy may be void)',
            'Missing council tax payment (debt collection)',
            'Not re-registering to vote (lost vote)',
        ],
        'follow_up_dates': [
            'Check new council tax band within 2 months',
            'Verify driving licence arrives with correct address',
            'Confirm car insurance reflects new address',
        ],
        'verification_summary': {
            'total_steps': total,
            'verified': verified_count,
            'not_verified': total - verified_count,
            'truth_class': 'CONCEPTUAL',
        },
    }
    return _truth_wrap('move_house', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages. Source URLs provided but content not checked."])


def manage_car(registration):
    state = _load_state('cars.json')
    car = state.get(registration, {
        'registration': registration,
        'mot_expiry': None,
        'tax_expiry': None,
        'v5c_received': None,
        'last_check': None,
        'recalls_acknowledged': [],
        'reminders_set': [],
    })

    now = datetime.now().strftime('%Y-%m-%d')
    car['last_check'] = now
    state[registration] = car
    _save_state('cars.json', state)

    renewals = []
    if car.get('mot_expiry'):
        mot_dt = datetime.strptime(car['mot_expiry'], '%Y-%m-%d')
        days_to_mot = (mot_dt - datetime.now()).days
        renewals.append({
            'item': 'MOT',
            'expiry': car['mot_expiry'],
            'days_remaining': days_to_mot,
            'action_class': 'USER_HANDOFF' if days_to_mot < 0 else 'APPROVAL_REQUIRED',
            'urgent': days_to_mot <= 30,
            'source_url': 'https://www.gov.uk/get-mot',
        })
    else:
        renewals.append({
            'item': 'MOT',
            'expiry': 'Unknown',
            'action_class': 'APPROVAL_REQUIRED',
            'urgent': False,
            'source_url': 'https://www.gov.uk/check-mot-history',
        })

    if car.get('tax_expiry'):
        tax_dt = datetime.strptime(car['tax_expiry'], '%Y-%m-%d')
        days_to_tax = (tax_dt - datetime.now()).days
        renewals.append({
            'item': 'Road tax',
            'expiry': car['tax_expiry'],
            'days_remaining': days_to_tax,
            'action_class': 'APPROVAL_REQUIRED',
            'urgent': days_to_tax <= 30,
            'source_url': 'https://www.gov.uk/vehicle-tax',
        })
    else:
        renewals.append({
            'item': 'Road tax',
            'expiry': 'Unknown',
            'action_class': 'APPROVAL_REQUIRED',
            'urgent': False,
            'source_url': 'https://www.gov.uk/check-vehicle-tax',
        })

    workflow_steps = [
        _step_with_verification(1, 'Check MOT status', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-mot-history', verification_method='none'),
        _step_with_verification(2, 'Check vehicle tax status', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-vehicle-tax', verification_method='none'),
        _step_with_verification(3, 'Check for recalls', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-vehicle-recalls', verification_method='none'),
        _step_with_verification(4, 'Verify insurance is current', 'USER_HANDOFF',
            '', verification_method='none'),
        _step_with_verification(5, 'Check V5C is correct', 'USER_HANDOFF',
            '', verification_method='none'),
    ]

    result = {
        'status': 'ok',
        'task': f'Manage car {registration}',
        'capability_level': 4,
        'workflow_steps': workflow_steps,
        'agent_actions': ['Check MOT history', 'Check tax status', 'Check recalls', 'Set renewal reminders'],
        'user_actions': ['Book MOT appointment', 'Arrange insurance', 'Keep V5C up to date', 'Fix any advisories'],
        'required_documents': ['V5C registration certificate', 'MOT certificate', 'Insurance certificate'],
        'deadlines': [
            f'MOT expiry: {car.get("mot_expiry", "unknown")}',
            f'Tax expiry: {car.get("tax_expiry", "unknown")}',
        ],
        'fees': ['MOT: max 54.85 (cars)', 'Road tax: varies by vehicle'],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Driving without valid MOT (fine up to 2,500, 3 penalty points)',
            'Driving without road tax (fine up to 5,000, vehicle clamped)',
            'Ignoring recalls (safety risk)',
            'Insurance invalidated by vehicle changes',
        ],
        'follow_up_dates': renewals,
        'current_state': car,
        'verification_summary': {
            'total_steps': len(workflow_steps),
            'verified': sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow_steps if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('manage_car', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def onboard_car(registration):
    workflow_steps = [
        _step_with_verification(1, 'Check MOT history', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-mot-history', verification_method='none',
            fee='Free'),
        _step_with_verification(2, 'Check vehicle tax', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-vehicle-tax', verification_method='none',
            fee='Free'),
        _step_with_verification(3, 'Check for safety recalls', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/check-vehicle-recalls', verification_method='none',
            fee='Free'),
        _step_with_verification(4, 'Transfer V5C registration', 'USER_HANDOFF',
            'https://www.gov.uk/sold-bought-vehicle', verification_method='none',
            fee='Free', deadline='As soon as possible'),
        _step_with_verification(5, 'Get insurance', 'USER_HANDOFF',
            '', verification_method='none',
            fee='Varies', deadline='Before driving the car'),
        _step_with_verification(6, 'Tax the vehicle', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/vehicle-tax', verification_method='none',
            fee='Varies', dependency='step_4 and step_5'),
        _step_with_verification(7, 'Get an MOT (if needed)', 'USER_HANDOFF',
            'https://www.gov.uk/get-mot', verification_method='none',
            fee='Up to 54.85'),
        _step_with_verification(8, 'Update your insurance address', 'USER_HANDOFF',
            '', verification_method='none'),
        _step_with_verification(9, 'Keep all documents safe', 'USER_HANDOFF',
            '', verification_method='none'),
    ]

    result = {
        'status': 'ok',
        'task': f'Onboard used car {registration}',
        'capability_level': 4,
        'workflow_steps': workflow_steps,
        'agent_actions': ['Check MOT history', 'Check tax status', 'Check recalls', 'Help transfer V5C online'],
        'user_actions': ['Get insurance before driving', 'Complete V5C transfer section 6', 'Book MOT if needed', 'Store documents safely'],
        'required_documents': ['V5C registration certificate (from seller)', 'Insurance certificate', 'MOT certificate'],
        'deadlines': [
            'Insurance: must be in place before driving',
            'V5C transfer: as soon as possible after purchase',
            'Tax: must be valid before driving on public roads',
        ],
        'fees': [
            'MOT: up to 54.85',
            'Road tax: varies by vehicle CO2 emissions and age',
            'Insurance: varies widely',
        ],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Driving without insurance (fine, points, vehicle seized)',
            'Driving without tax (fine up to 5,000)',
            'Driving without valid MOT (fine up to 2,500, 3 points)',
            'Not transferring V5C (legal liability as registered keeper)',
        ],
        'follow_up_dates': [
            'Check MOT expiry - book renewal before it expires',
            'Check tax expiry - renew before it expires',
            'Schedule first service if no service history',
        ],
        'verification_summary': {
            'total_steps': len(workflow_steps),
            'verified': sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow_steps if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('onboard_car', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def manage_business(company_number):
    state = _load_state('companies.json')
    company = state.get(company_number, {
        'company_number': company_number,
        'confirmation_statement_due': None,
        'accounts_due': None,
        'corporation_tax_due': None,
        'vat_returns': [],
        'last_check': None,
    })

    now = datetime.now().strftime('%Y-%m-%d')
    company['last_check'] = now
    state[company_number] = company
    _save_state('companies.json', state)

    deadlines = []
    if company.get('confirmation_statement_due'):
        deadlines.append({
            'filing': 'Confirmation Statement',
            'deadline': company['confirmation_statement_due'],
            'authority': 'Companies House',
            'source_url': 'https://www.gov.uk/file-confirmation-statement',
            'fee': '13 online',
            'penalty': 'Company can be struck off',
        })
    if company.get('accounts_due'):
        deadlines.append({
            'filing': 'Annual Accounts',
            'deadline': company['accounts_due'],
            'authority': 'Companies House',
            'source_url': 'https://www.gov.uk/file-company-accounts',
            'fee': 'Free',
            'penalty': 'Up to 7,500 for private company',
        })
    if company.get('corporation_tax_due'):
        deadlines.append({
            'filing': 'Corporation Tax Return',
            'deadline': company['corporation_tax_due'],
            'authority': 'HMRC',
            'source_url': 'https://www.gov.uk/file-company-tax-return',
            'fee': 'Free',
            'penalty': 'Automatic 100, escalating',
        })

    workflow_steps = [
        _step_with_verification(1, 'File Confirmation Statement annually', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/file-confirmation-statement', verification_method='none',
            deadline='Every year, within 14 days of anniversary'),
        _step_with_verification(2, 'File Annual Accounts', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/file-company-accounts', verification_method='none',
            deadline='9 months after accounting period end'),
        _step_with_verification(3, 'File Corporation Tax Return', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/file-company-tax-return', verification_method='none',
            deadline='12 months after accounting period end'),
        _step_with_verification(4, 'Pay Corporation Tax', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/pay-corporation-tax', verification_method='none',
            deadline='9 months and 1 day after accounting period end'),
        _step_with_verification(5, 'VAT returns (if registered)', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/vat-returns', verification_method='none',
            deadline='Quarterly'),
        _step_with_verification(6, 'Update Companies House records', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/update-company-information', verification_method='none'),
        _step_with_verification(7, 'Maintain PSC register', 'USER_HANDOFF',
            '', verification_method='none'),
    ]

    result = {
        'status': 'ok',
        'task': f'Manage company {company_number}',
        'capability_level': 5,
        'workflow_steps': workflow_steps,
        'agent_actions': ['File Confirmation Statement', 'Prepare accounts template', 'Calculate Corporation Tax', 'Submit VAT returns', 'File tax returns'],
        'user_actions': ['Approve financial accounts', 'Approve tax filings', 'Keep board minutes', 'Maintain PSC register'],
        'required_documents': ['Company accounts', 'Corporation tax computation', 'Confirmation statement data', 'VAT records (if registered)'],
        'deadlines': deadlines,
        'fees': [
            'Confirmation Statement: 13 online',
            'Company accounts: Free',
            'Corporation Tax Return: Free',
            'Late filing penalties: 100-7,500+',
        ],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Missing Confirmation Statement deadline (company struck off)',
            'Late accounts filing (automatic penalties)',
            'Late Corporation Tax Return (automatic 100, escalating)',
            'Not maintaining PSC register (criminal offence)',
            'Failing to notify Companies House of changes (fine up to 5,000)',
        ],
        'follow_up_dates': [
            'Confirmation Statement: annual, within 14 days of incorporation anniversary',
            'Accounts: 9 months after accounting period end',
            'Corporation Tax: 9 months and 1 day after accounting period end',
            'Tax Return: 12 months after accounting period end',
            'VAT returns: quarterly',
        ],
        'current_state': company,
        'verification_summary': {
            'total_steps': len(workflow_steps),
            'verified': sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow_steps if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('manage_business', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def change_details_everywhere(detail_type, old_value, new_value):
    if detail_type.lower() not in ('name', 'address'):
        result = {'status': 'error', 'message': 'detail_type must be "name" or "address"'}
        return _truth_wrap('change_details_everywhere', result, truth_class="VERIFIED",
                          confidence=1.0, limitations=["Invalid input"])

    orgs = []
    if detail_type.lower() == 'name':
        orgs = [
            {'org': 'DVLA - Driving Licence', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/change-driving-licence/details', 'fee': 'Free'},
            {'org': 'HMRC - Tax records', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/update-hmrc-your-personal-details', 'fee': 'Free'},
            {'org': 'HM Passport Office', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/renew-adult-passport', 'fee': '82.50', 'note': 'Name change requires passport renewal'},
            {'org': 'Banks and building societies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Electoral roll', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/register-to-vote', 'fee': 'Free'},
            {'org': 'NHS - GP registration', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'DVLA - Vehicle tax', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/vehicle-tax', 'fee': 'Free'},
            {'org': 'Employer / payroll', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Pension providers', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Insurance policies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'HM Land Registry (if property owner)', 'action_class': 'USER_HANDOFF', 'fee': 'Varies'},
        ]
    else:
        orgs = [
            {'org': 'DVLA - Driving Licence', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/change-address-driving-licence', 'fee': 'Free'},
            {'org': 'DVLA - Vehicle tax', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/vehicle-tax', 'fee': 'Free'},
            {'org': 'HMRC - Tax records', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/update-hmrc-your-personal-details', 'fee': 'Free'},
            {'org': 'Electoral roll', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/register-to-vote', 'fee': 'Free'},
            {'org': 'Council tax', 'action_class': 'USER_HANDOFF', 'source_url': 'https://www.gov.uk/find-local-council', 'fee': 'Free'},
            {'org': 'Banks and building societies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'NHS - GP registration', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Insurance policies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Employer / payroll', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'HMRC - National Insurance record', 'action_class': 'APPROVAL_REQUIRED', 'source_url': 'https://www.gov.uk/personal-tax-account', 'fee': 'Free'},
            {'org': 'HM Land Registry (if property owner)', 'action_class': 'USER_HANDOFF', 'fee': 'Varies'},
            {'org': 'Student loan company', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
        ]

    for i, org in enumerate(orgs):
        org['step'] = i + 1
        if org.get('source_url'):
            org['source_hash'] = _make_source_hash(org['source_url'])
        org['verification_status'] = 'NOT_VERIFIED — source_url provided but not checked' if org.get('source_url') else 'N/A'
        org['verification_method'] = 'none'

    agent_items = [o for o in orgs if o['action_class'] in ('AUTO', 'APPROVAL_REQUIRED')]
    user_items = [o for o in orgs if o['action_class'] == 'USER_HANDOFF']

    result = {
        'status': 'ok',
        'task': f'Change {detail_type} everywhere',
        'capability_level': 5,
        'workflow_steps': orgs,
        'agent_actions': [o['org'] for o in agent_items],
        'user_actions': [o['org'] for o in user_items],
        'required_documents': [
            'Deed poll or marriage certificate (for name change)',
            'Proof of new address (for address change)',
            'Current driving licence',
        ],
        'deadlines': [
            'DVLA address change: within 8 weeks',
            'Electoral roll: register promptly',
            'Council tax: notify immediately',
        ],
        'fees': ['Passport renewal (name change): 82.50', 'All other updates: Free'],
        'official_urls': [o['source_url'] for o in orgs if o.get('source_url')],
        'failure_modes': [
            'Missed organisation leads to communications going to wrong address',
            'Driving licence with wrong name/address is not valid ID',
            'HMRC mismatch causes tax code errors',
            'Insurance invalidated by unreported change',
        ],
        'follow_up_dates': [
            'Verify all updates within 4 weeks',
            'Check HMRC tax code reflects changes',
            'Confirm electoral roll registration',
        ],
        'old_value': old_value,
        'new_value': new_value,
        'verification_summary': {
            'total_steps': len(orgs),
            'verified': sum(1 for o in orgs if o['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for o in orgs if 'NOT_VERIFIED' in str(o['verification_status'])),
        },
    }
    return _truth_wrap('change_details_everywhere', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": o['source_url']} for o in orgs if o.get('source_url')],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def renew_passport():
    workflow_steps = [
        _step_with_verification(1, 'Check passport eligibility for online renewal', 'AUTO',
            'https://www.gov.uk/renew-adult-passport', verification_method='none'),
        _step_with_verification(2, 'Get a digital photo', 'USER_HANDOFF',
            'https://www.gov.uk/passport-photo-guidelines', verification_method='none'),
        _step_with_verification(3, 'Complete online application', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/renew-adult-passport', verification_method='none'),
        _step_with_verification(4, 'Pay for renewal', 'APPROVAL_REQUIRED',
            '', verification_method='none',
            fee='82.50 online / 92.50 with Check & Send'),
        _step_with_verification(5, 'Post old passport', 'USER_HANDOFF',
            '', verification_method='none'),
        _step_with_verification(6, 'Wait for new passport', 'USER_HANDOFF',
            '', verification_method='none',
            takes='Up to 10 weeks'),
        _step_with_verification(7, 'Sign new passport immediately', 'USER_HANDOFF',
            '', verification_method='none'),
    ]

    result = {
        'status': 'ok',
        'task': 'Renew passport',
        'capability_level': 3,
        'workflow_steps': workflow_steps,
        'agent_actions': ['Guide application process', 'Check photo meets requirements', 'Pre-fill form details'],
        'user_actions': ['Get digital photo taken', 'Pay for renewal', 'Post old passport', 'Sign new passport'],
        'required_documents': ['Current passport', 'Digital photo', 'Payment method'],
        'deadlines': [
            'Renew at least 10 weeks before travel',
            'Some countries require 6 months validity on passport',
        ],
        'fees': [
            'Online renewal: 82.50',
            'Post Office Check & Send: 92.50',
            'Urgent appointment: 193.50',
        ],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Photo does not meet requirements (application delayed)',
            'Not signing new passport (invalid document)',
            'Underestimating processing time (missed travel)',
        ],
        'follow_up_dates': [
            'Set reminder: check passport 6 months before international travel',
            'Set reminder: renew 10 weeks before expiry',
        ],
        'verification_summary': {
            'total_steps': len(workflow_steps),
            'verified': sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow_steps if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('renew_passport', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def start_driving():
    workflow_steps = [
        _step_with_verification(1, 'Apply for provisional driving licence', 'APPROVAL_REQUIRED',
            'https://www.gov.uk/apply-first-provisional-driving-licence', verification_method='none',
            fee='34 online / 43 by post', takes='Up to 3 weeks'),
        _step_with_verification(2, 'Book and take theory test', 'USER_HANDOFF',
            'https://www.gov.uk/book-driving-test', verification_method='none',
            fee='23', prereq='Provisional licence in hand'),
        _step_with_verification(3, 'Book and take practical driving test', 'USER_HANDOFF',
            'https://www.gov.uk/book-driving-test', verification_method='none',
            fee='62 weekday / 75 weekend', prereq='Passed theory test'),
        _step_with_verification(4, 'Receive full driving licence', 'USER_HANDOFF',
            '', verification_method='none',
            takes='About 3 weeks after passing'),
    ]

    result = {
        'status': 'ok',
        'task': 'Start driving - provisional to full licence',
        'capability_level': 3,
        'workflow_steps': workflow_steps,
        'agent_actions': ['Guide provisional licence application', 'Explain theory test format', 'Explain practical test format', 'Help book tests'],
        'user_actions': ['Apply for provisional licence', 'Study for theory test', 'Take theory test', 'Have driving lessons', 'Take practical test', 'Receive full licence'],
        'required_documents': ['Identity document', 'Address history (3 years)', 'National Insurance number', 'Passport-style photo'],
        'deadlines': [
            'Theory test valid for 2 years from passing date',
            'Must pass practical within 2 years of theory',
            'Provisional licence: apply up to 3 months before 17th birthday',
        ],
        'fees': [
            'Provisional licence: 34 online / 43 by post',
            'Theory test: 23',
            'Practical test: 62 weekday / 75 evenings/weekends/bank holidays',
            'Total minimum: 119 (online) to 141 (by post, weekday test)',
        ],
        'official_urls': [s['source_url'] for s in workflow_steps if s['source_url']],
        'failure_modes': [
            'Provisional licence application rejected (wrong documents)',
            'Theory test failed (must retake, fee again)',
            'Practical test failed (must retake, fee again)',
            'Driving on provisional without L plates (fine + points)',
            'Driving on motorway on provisional (illegal)',
        ],
        'follow_up_dates': [
            'Theory test: book when ready, valid 2 years',
            'Practical test: book after passing theory, within 2 years',
        ],
        'verification_summary': {
            'total_steps': len(workflow_steps),
            'verified': sum(1 for s in workflow_steps if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow_steps if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('start_driving', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow_steps if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def start_regulated_business(business_type):
    business_lower = business_type.lower().strip()

    workflows = {
        'food': {
            'name': 'Food Business Registration',
            'authority': 'Local Council Environmental Health',
            'source_url': 'https://www.gov.uk/starting-food-business',
            'fee': 'Free',
            'deadline': 'At least 28 days before opening',
            'steps': [
                _step_with_verification(1, 'Register food business with local council', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/starting-food-business', verification_method='none', fee='Free'),
                _step_with_verification(2, 'Create a Food Safety Management System', 'USER_HANDOFF',
                    'https://www.food.gov.uk/business-guidance/starting-up', verification_method='none'),
                _step_with_verification(3, 'Get food hygiene rating assessment', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(4, 'Ensure premises meet regulations', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(5, 'Staff food hygiene training', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(6, 'Allergen information compliance', 'USER_HANDOFF',
                    'https://www.food.gov.uk/allergens', verification_method='none'),
            ],
        },
        'premises': {
            'name': 'Licensed Premises (Alcohol/Selling Late)',
            'authority': 'Local Council Licensing',
            'source_url': 'https://www.gov.uk/find-licences/premises-licence',
            'fee': '100-635 (based on rateable value)',
            'deadline': 'Apply before opening',
            'steps': [
                _step_with_verification(1, 'Apply for premises licence', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/find-licences/premises-licence', verification_method='none', fee='100-635'),
                _step_with_verification(2, 'Designate a Designated Premises Supervisor (DPS)', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(3, 'Apply for personal licence (DPS)', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/find-licences/personal-licence', verification_method='none', fee='37'),
                _step_with_verification(4, 'Complete licensing objectives training', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(5, 'Display licence and notices', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(6, 'Notify responsible authorities', 'AUTO',
                    '', verification_method='none'),
            ],
        },
        'taxi': {
            'name': 'Private Hire / Taxi Driver Licence',
            'authority': 'Local Council',
            'source_url': 'https://www.gov.uk/private-hire-vehicle-licence',
            'fee': 'Varies by council',
            'deadline': 'Before driving',
            'steps': [
                _step_with_verification(1, 'Apply for private hire driver licence', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/private-hire-vehicle-licence', verification_method='none', fee='Varies'),
                _step_with_verification(2, 'DBS check', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(3, 'Medical examination', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(4, 'Topographical test', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(5, 'Driving test (if required)', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(6, 'Apply for vehicle licence', 'APPROVAL_REQUIRED',
                    '', verification_method='none', fee='Varies'),
            ],
        },
        'construction': {
            'name': 'Construction Business',
            'authority': 'HSE / Local Council',
            'source_url': 'https://www.hse.gov.uk/construction/',
            'fee': 'Free registration',
            'deadline': 'Before starting work',
            'steps': [
                _step_with_verification(1, 'Register as a construction business', 'APPROVAL_REQUIRED',
                    'https://www.hse.gov.uk/construction/', verification_method='none', fee='Free'),
                _step_with_verification(2, 'Health and safety policy', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(3, 'Public liability insurance', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(4, 'CSCS cards for workers', 'USER_HANDOFF',
                    'https://www.cscs.co.uk/', verification_method='none'),
                _step_with_verification(5, 'Waste carrier licence', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/guidance/register-as-a-waste-carrier', verification_method='none',
                    fee='154 for 3 years'),
            ],
        },
    }

    workflow = workflows.get(business_lower)
    if not workflow:
        result = {'status': 'error', 'message': f'Unknown business type: {business_type}', 'available_types': list(workflows.keys())}
        return _truth_wrap('start_regulated_business', result, truth_class="VERIFIED",
                          confidence=1.0, limitations=["Invalid input"])

    agent_items = [s for s in workflow['steps'] if s['action_class'] in ('AUTO', 'APPROVAL_REQUIRED')]
    user_items = [s for s in workflow['steps'] if s['action_class'] == 'USER_HANDOFF']

    result = {
        'status': 'ok',
        'task': f'Start regulated business: {workflow["name"]}',
        'capability_level': 3,
        'workflow_steps': workflow['steps'],
        'agent_actions': [s['task'] for s in agent_items],
        'user_actions': [s['task'] for s in user_items],
        'required_documents': ['Business plan', 'Premises details', 'Insurance documents', 'Staff training records'],
        'deadlines': [f'{workflow["name"]}: {workflow["deadline"]}'],
        'fees': [f'{workflow["name"]}: {workflow["fee"]}'],
        'official_urls': [s['source_url'] for s in workflow['steps'] if s['source_url']],
        'failure_modes': [
            'Operating without registration (criminal offence, unlimited fine)',
            'Failing inspection (can be shut down)',
            'Not meeting fire safety requirements (prosecution)',
            'Serving food without registration (fine up to 5,000)',
        ],
        'follow_up_dates': [
            'Inspect premises before council visit',
            'Renew licence before expiry',
            'Annual food hygiene rating reassessment',
        ],
        'verification_summary': {
            'total_steps': len(workflow['steps']),
            'verified': sum(1 for s in workflow['steps'] if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow['steps'] if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('start_regulated_business', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow['steps'] if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages"])


def resolve_letter(letter_text):
    text_lower = letter_text.lower()

    patterns = {
        'tax_bill': ['tax bill', 'tax payment', 'self assessment', 'pay tax', 'hmrc', 'tax due', 'underpayment'],
        'mot_expiry': ['mot', 'mot test', 'vehicle test', 'mot expired', 'mot due'],
        'tax_expiry': ['vehicle tax', 'road tax', 'car tax', 'tax expires', 'tax due'],
        'passport_expiry': ['passport', 'passport renewal', 'passport expires'],
        'council_tax': ['council tax', 'council tax bill', 'council tax due'],
        'driving_licence': ['driving licence', 'licence renewal', 'dvla'],
        'company_filing': ['confirmation statement', 'annual accounts', 'companies house', 'company filing'],
        'benefits': ['universal credit', 'child benefit', 'pip', 'esa', 'benefit'],
        'insurance': ['insurance', 'insurance renewal', 'insurance expires'],
        'court_fine': ['court fine', 'penalty', 'fixed penalty', 'fine'],
        'v5c': ['v5c', 'vehicle registration', 'logbook'],
        'electoral': ['electoral', 'voting', 'register to vote'],
        'medical': ['nhs', 'gp', 'medical', 'hospital'],
    }

    matched = []
    for category, keywords in patterns.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(category)
                break

    if not matched:
        matched = ['unknown']

    workflows = {
        'tax_bill': {
            'task': 'Resolve HMRC tax bill',
            'capability_level': 4,
            'workflow_steps': [
                _step_with_verification(1, 'Identify amount and deadline', 'AUTO', '', verification_method='none'),
                _step_with_verification(2, 'Check if amount is correct', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/check-income-tax-returns', verification_method='none'),
                _step_with_verification(3, 'Set up payment plan if needed', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/pay-self-assessment-tax-bill', verification_method='none'),
                _step_with_verification(4, 'Dispute if incorrect', 'USER_HANDOFF',
                    'https://www.gov.uk/claim-tax-refund', verification_method='none'),
            ],
            'agent_actions': ['Identify deadline and amount', 'Check tax account', 'Set up payment plan'],
            'user_actions': ['Approve payment', 'Provide bank details', 'Dispute if needed'],
        },
        'mot_expiry': {
            'task': 'Renew MOT',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Check current MOT status', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/check-mot-history', verification_method='none'),
                _step_with_verification(2, 'Book MOT test', 'USER_HANDOFF',
                    'https://www.gov.uk/get-mot', verification_method='none'),
                _step_with_verification(3, 'Take vehicle to test', 'USER_HANDOFF',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Check MOT status', 'Find local garages'],
            'user_actions': ['Book test', 'Take vehicle', 'Pay garage'],
        },
        'tax_expiry': {
            'task': 'Renew vehicle tax',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Check vehicle tax status', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/check-vehicle-tax', verification_method='none'),
                _step_with_verification(2, 'Ensure valid MOT', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(3, 'Tax vehicle online', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/vehicle-tax', verification_method='none'),
            ],
            'agent_actions': ['Check tax status', 'Verify MOT validity'],
            'user_actions': ['Pay for tax renewal'],
        },
        'passport_expiry': {
            'task': 'Renew passport',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Check eligibility for online renewal', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Get digital photo', 'USER_HANDOFF',
                    '', verification_method='none'),
                _step_with_verification(3, 'Apply online', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/renew-adult-passport', verification_method='none'),
                _step_with_verification(4, 'Post old passport', 'USER_HANDOFF',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Check eligibility', 'Guide application'],
            'user_actions': ['Get photo', 'Pay', 'Post documents'],
        },
        'council_tax': {
            'task': 'Handle council tax matter',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Identify council and issue', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Contact council', 'USER_HANDOFF',
                    'https://www.gov.uk/find-local-council', verification_method='none'),
                _step_with_verification(3, 'Check for discounts or exemptions', 'APPROVAL_REQUIRED',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Find council contact', 'Check for discounts'],
            'user_actions': ['Contact council', 'Provide evidence'],
        },
        'driving_licence': {
            'task': 'Handle driving licence matter',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Identify specific issue', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Follow DVLA guidance', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/browse/driving', verification_method='none'),
                _step_with_verification(3, 'Submit required forms', 'APPROVAL_REQUIRED',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Identify issue', 'Guide process'],
            'user_actions': ['Submit forms', 'Provide documents'],
        },
        'company_filing': {
            'task': 'Handle company filing matter',
            'capability_level': 4,
            'workflow_steps': [
                _step_with_verification(1, 'Identify filing requirement', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Prepare documents', 'APPROVAL_REQUIRED',
                    '', verification_method='none'),
                _step_with_verification(3, 'File with Companies House', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/file-confirmation-statement', verification_method='none'),
            ],
            'agent_actions': ['Identify requirement', 'Prepare templates'],
            'user_actions': ['Approve accounts', 'Authorise filing'],
        },
        'benefits': {
            'task': 'Handle benefits matter',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Identify benefit and action required', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Check eligibility', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/benefits-calculators', verification_method='none'),
                _step_with_verification(3, 'Contact DWP or apply', 'USER_HANDOFF',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Identify benefit', 'Check calculator'],
            'user_actions': ['Contact DWP', 'Provide information'],
        },
        'insurance': {
            'task': 'Handle insurance matter',
            'capability_level': 2,
            'workflow_steps': [
                _step_with_verification(1, 'Identify type of insurance', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Check renewal date', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(3, 'Compare or renew', 'USER_HANDOFF',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Identify renewal date', 'Compare options'],
            'user_actions': ['Make final decision', 'Pay'],
        },
        'court_fine': {
            'task': 'Handle court fine or penalty',
            'capability_level': 2,
            'workflow_steps': [
                _step_with_verification(1, 'Identify fine amount and deadline', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Check if you can appeal', 'APPROVAL_REQUIRED',
                    '', verification_method='none'),
                _step_with_verification(3, 'Pay or set up payment plan', 'APPROVAL_REQUIRED',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Identify details', 'Check appeal options'],
            'user_actions': ['Decide to pay or appeal', 'Pay'],
        },
        'v5c': {
            'task': 'Handle V5C matter',
            'capability_level': 3,
            'workflow_steps': [
                _step_with_verification(1, 'Identify V5C issue', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Contact DVLA', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/vehicle-registration', verification_method='none'),
                _step_with_verification(3, 'Order replacement if needed', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/vehicle-registration', verification_method='none', fee='Free'),
            ],
            'agent_actions': ['Identify issue', 'Guide DVLA process'],
            'user_actions': ['Contact DVLA', 'Provide details'],
        },
        'electoral': {
            'task': 'Handle electoral matter',
            'capability_level': 2,
            'workflow_steps': [
                _step_with_verification(1, 'Identify issue', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Register or update', 'APPROVAL_REQUIRED',
                    'https://www.gov.uk/register-to-vote', verification_method='none'),
            ],
            'agent_actions': ['Identify issue', 'Guide registration'],
            'user_actions': ['Provide NI number', 'Confirm address'],
        },
        'medical': {
            'task': 'Handle NHS/medical matter',
            'capability_level': 1,
            'workflow_steps': [
                _step_with_verification(1, 'Identify issue', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Direct to appropriate NHS service', 'AUTO',
                    'https://www.nhs.uk', verification_method='none'),
            ],
            'agent_actions': ['Identify service', 'Provide NHS links'],
            'user_actions': ['Contact service directly'],
        },
        'unknown': {
            'task': 'Unclear government letter',
            'capability_level': 1,
            'workflow_steps': [
                _step_with_verification(1, 'Scan letter for sender name and logo', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(2, 'Check for reference numbers', 'AUTO',
                    '', verification_method='none'),
                _step_with_verification(3, 'Contact sender to clarify', 'USER_HANDOFF',
                    '', verification_method='none'),
            ],
            'agent_actions': ['Help identify sender'],
            'user_actions': ['Contact sender', 'Provide letter details'],
        },
    }

    primary = matched[0]
    workflow = workflows.get(primary, workflows['unknown'])

    result = {
        'status': 'ok',
        'task': workflow['task'],
        'capability_level': workflow['capability_level'],
        'identified_categories': matched,
        'workflow_steps': workflow['workflow_steps'],
        'agent_actions': workflow.get('agent_actions', []),
        'user_actions': workflow.get('user_actions', []),
        'required_documents': ['The original letter', 'Any reference numbers', 'Personal identification'],
        'deadlines': ['Check the letter for any response deadlines'],
        'fees': [],
        'official_urls': [s['source_url'] for s in workflow['workflow_steps'] if s['source_url']],
        'failure_modes': [
            'Ignoring the letter (escalation, fines, legal action)',
            'Missing response deadline',
            'Responding to scam letter (verify sender)',
        ],
        'follow_up_dates': [
            'Respond within any stated deadline',
            'Keep copy of letter and response',
        ],
        'letter_snippet': letter_text[:200] + ('...' if len(letter_text) > 200 else ''),
        'verification_summary': {
            'total_steps': len(workflow['workflow_steps']),
            'verified': sum(1 for s in workflow['workflow_steps'] if s['verification_status'] == 'VERIFIED'),
            'not_verified': sum(1 for s in workflow['workflow_steps'] if s['verification_status'] != 'VERIFIED'),
        },
    }
    return _truth_wrap('resolve_letter', result, truth_class="CONCEPTUAL",
                      confidence=0.2,
                      evidence=[{"type": "source_url", "url": s['source_url']} for s in workflow['workflow_steps'] if s['source_url']],
                      limitations=["Steps not yet verified against live GOV.UK pages. Letter parsing is pattern-based."])


def admin_audit(current_state):
    checks = []
    now = datetime.now()

    if isinstance(current_state, str):
        try:
            current_state = json.loads(current_state)
        except (json.JSONDecodeError, TypeError):
            current_state = {}

    if not current_state:
        result = {
            'status': 'ok',
            'task': 'Admin audit',
            'capability_level': 4,
            'message': 'No state data provided. Supply your details for a personalised audit.',
            'suggested_info': [
                'Vehicle registrations you own',
                'Passport expiry date',
                'Driving licence expiry date',
                'Company number(s) if applicable',
                'When you last filed Self Assessment',
                'Insurance renewal dates',
                'V5C details for vehicles',
            ],
            'workflow_steps': [],
            'agent_actions': [],
            'user_actions': [],
            'required_documents': [],
            'deadlines': [],
            'fees': [],
            'official_urls': [],
            'failure_modes': [],
            'follow_up_dates': [],
        }
        return _truth_wrap('admin_audit', result, truth_class="CONCEPTUAL",
                          confidence=0.1,
                          limitations=["No data provided for audit"])

    if current_state.get('passport_expiry'):
        try:
            pp_exp = datetime.strptime(current_state['passport_expiry'], '%Y-%m-%d')
            days = (pp_exp - now).days
            checks.append({
                'item': 'Passport',
                'status': 'EXPIRED' if days < 0 else 'EXPIRING_SOON' if days < 180 else 'OK',
                'expiry': current_state['passport_expiry'],
                'days_remaining': days,
                'action_class': 'USER_HANDOFF' if days < 0 else 'APPROVAL_REQUIRED' if days < 180 else None,
            })
        except (ValueError, TypeError):
            pass

    if current_state.get('driving_licence_expiry'):
        try:
            dl_exp = datetime.strptime(current_state['driving_licence_expiry'], '%Y-%m-%d')
            days = (dl_exp - now).days
            checks.append({
                'item': 'Driving Licence',
                'status': 'EXPIRED' if days < 0 else 'EXPIRING_SOON' if days < 60 else 'OK',
                'expiry': current_state['driving_licence_expiry'],
                'days_remaining': days,
                'action_class': 'USER_HANDOFF' if days < 0 else 'APPROVAL_REQUIRED' if days < 60 else None,
            })
        except (ValueError, TypeError):
            pass

    if current_state.get('vehicles'):
        for reg, info in current_state['vehicles'].items():
            if info.get('mot_expiry'):
                try:
                    mot_exp = datetime.strptime(info['mot_expiry'], '%Y-%m-%d')
                    days = (mot_exp - now).days
                    checks.append({
                        'item': f'MOT ({reg})',
                        'status': 'EXPIRED' if days < 0 else 'EXPIRING_SOON' if days < 30 else 'OK',
                        'expiry': info['mot_expiry'],
                        'days_remaining': days,
                        'action_class': 'USER_HANDOFF' if days < 0 else 'APPROVAL_REQUIRED' if days < 30 else None,
                    })
                except (ValueError, TypeError):
                    pass
            if info.get('tax_expiry'):
                try:
                    tax_exp = datetime.strptime(info['tax_expiry'], '%Y-%m-%d')
                    days = (tax_exp - now).days
                    checks.append({
                        'item': f'Vehicle Tax ({reg})',
                        'status': 'EXPIRED' if days < 0 else 'EXPIRING_SOON' if days < 30 else 'OK',
                        'expiry': info['tax_expiry'],
                        'days_remaining': days,
                        'action_class': 'APPROVAL_REQUIRED' if days < 30 else None,
                    })
                except (ValueError, TypeError):
                    pass

    if current_state.get('company_number'):
        comp = manage_business(current_state['company_number'])
        for deadline in comp.get('result', {}).get('deadlines', []):
            if isinstance(deadline, dict) and deadline.get('deadline'):
                try:
                    dl = datetime.strptime(deadline['deadline'], '%Y-%m-%d')
                    days = (dl - now).days
                    checks.append({
                        'item': f"Company Filing: {deadline.get('filing', 'Unknown')}",
                        'status': 'OVERDUE' if days < 0 else 'DUE_SOON' if days < 30 else 'OK',
                        'expiry': deadline['deadline'],
                        'days_remaining': days,
                        'action_class': 'APPROVAL_REQUIRED' if days < 30 else None,
                    })
                except (ValueError, TypeError):
                    pass

    if current_state.get('insurance_renewals'):
        for ins in current_state['insurance_renewals']:
            try:
                ins_exp = datetime.strptime(ins.get('expiry', ''), '%Y-%m-%d')
                days = (ins_exp - now).days
                checks.append({
                    'item': f"Insurance: {ins.get('type', 'Unknown')}",
                    'status': 'EXPIRED' if days < 0 else 'EXPIRING_SOON' if days < 30 else 'OK',
                    'expiry': ins['expiry'],
                    'days_remaining': days,
                    'action_class': 'USER_HANDOFF',
                })
            except (ValueError, TypeError):
                pass

    if current_state.get('self_assessment_last_filed'):
        try:
            last = datetime.strptime(current_state['self_assessment_last_filed'], '%Y-%m-%d')
            if last.year < now.year:
                checks.append({
                    'item': 'Self Assessment Tax Return',
                    'status': 'POTENTIALLY_OVERDUE',
                    'note': f'Last filed {current_state["self_assessment_last_filed"]}',
                    'action_class': 'APPROVAL_REQUIRED',
                })
        except (ValueError, TypeError):
            pass

    overdue = [c for c in checks if c['status'] in ('EXPIRED', 'OVERDUE', 'POTENTIALLY_OVERDUE')]
    soon = [c for c in checks if c['status'] in ('EXPIRING_SOON', 'DUE_SOON')]
    ok = [c for c in checks if c['status'] == 'OK']

    result = {
        'status': 'ok',
        'task': 'Admin audit',
        'capability_level': 4,
        'workflow_steps': [],
        'agent_actions': ['Check vehicle tax', 'Check MOT status', 'Check company filings', 'Calculate deadlines'],
        'user_actions': ['Renew expired items', 'Approve payments', 'File overdue returns'],
        'required_documents': [],
        'deadlines': [f"{c['item']}: {c.get('expiry', 'unknown')} ({c['days_remaining']} days)" for c in checks if c.get('days_remaining') is not None],
        'fees': [],
        'official_urls': [
            'https://www.gov.uk/check-mot-history',
            'https://www.gov.uk/check-vehicle-tax',
            'https://www.gov.uk/renew-adult-passport',
            'https://www.gov.uk/renew-driving-licence',
        ],
        'failure_modes': [
            'Driving without MOT (fine + points)',
            'Driving without tax (fine + clamp)',
            'Expired passport (cannot travel)',
            'Overdue tax return (automatic penalties)',
        ],
        'follow_up_dates': [c for c in checks if c.get('days_remaining') is not None and c['days_remaining'] < 90],
        'audit_summary': {
            'total_items': len(checks),
            'overdue': len(overdue),
            'expiring_soon': len(soon),
            'ok': len(ok),
            'items': checks,
        },
    }
    return _truth_wrap('admin_audit', result, truth_class="DERIVED",
                      confidence=0.7,
                      evidence=[{"type": "user_input", "description": "current_state provided by user"}],
                      limitations=["Audit based on user-provided dates, not live API checks"])


def renewals(days_ahead):
    try:
        days = int(days_ahead)
    except (ValueError, TypeError):
        days = 30

    state = _load_state('cars.json')
    company_state = _load_state('companies.json')

    now = datetime.now()
    cutoff = now + timedelta(days=days)

    expiring = []

    for reg, car in state.items():
        if car.get('mot_expiry'):
            try:
                mot_dt = datetime.strptime(car['mot_expiry'], '%Y-%m-%d')
                if now <= mot_dt <= cutoff:
                    days_left = (mot_dt - now).days
                    expiring.append({
                        'item': f'MOT ({reg})',
                        'expiry': car['mot_expiry'],
                        'days_remaining': days_left,
                        'action_class': 'USER_HANDOFF',
                        'source_url': 'https://www.gov.uk/get-mot',
                        'fee': 'Up to 54.85',
                    })
            except (ValueError, TypeError):
                pass
        if car.get('tax_expiry'):
            try:
                tax_dt = datetime.strptime(car['tax_expiry'], '%Y-%m-%d')
                if now <= tax_dt <= cutoff:
                    days_left = (tax_dt - now).days
                    expiring.append({
                        'item': f'Vehicle Tax ({reg})',
                        'expiry': car['tax_expiry'],
                        'days_remaining': days_left,
                        'action_class': 'APPROVAL_REQUIRED',
                        'source_url': 'https://www.gov.uk/vehicle-tax',
                        'fee': 'Varies by vehicle',
                    })
            except (ValueError, TypeError):
                pass

    for comp_num, comp in company_state.items():
        for key in ['confirmation_statement_due', 'accounts_due', 'corporation_tax_due']:
            if comp.get(key):
                try:
                    dl_dt = datetime.strptime(comp[key], '%Y-%m-%d')
                    if now <= dl_dt <= cutoff:
                        days_left = (dl_dt - now).days
                        labels = {
                            'confirmation_statement_due': 'Confirmation Statement',
                            'accounts_due': 'Annual Accounts',
                            'corporation_tax_due': 'Corporation Tax Return',
                        }
                        expiring.append({
                            'item': f'{labels.get(key, key)} ({comp_num})',
                            'expiry': comp[key],
                            'days_remaining': days_left,
                            'action_class': 'APPROVAL_REQUIRED',
                            'source_url': 'https://www.gov.uk/file-confirmation-statement',
                        })
                except (ValueError, TypeError):
                    pass

    expiring.sort(key=lambda x: x.get('days_remaining', 9999))

    result = {
        'status': 'ok',
        'task': f'Renewals in next {days} days',
        'capability_level': 4,
        'workflow_steps': [],
        'agent_actions': ['Check all renewal dates', 'Calculate days remaining', 'Prioritise by urgency'],
        'user_actions': ['Renew expiring items', 'Approve payments', 'Book appointments'],
        'required_documents': [],
        'deadlines': [f"{e['item']}: {e['expiry']} ({e['days_remaining']} days)" for e in expiring],
        'fees': [],
        'official_urls': [
            'https://www.gov.uk/get-mot',
            'https://www.gov.uk/vehicle-tax',
            'https://www.gov.uk/renew-adult-passport',
            'https://www.gov.uk/renew-driving-licence',
            'https://www.gov.uk/file-confirmation-statement',
            'https://www.gov.uk/file-company-accounts',
        ],
        'failure_modes': [
            'Missing renewal deadlines',
            'Late filing penalties',
            'Invalid documents',
        ],
        'follow_up_dates': expiring,
        'count': len(expiring),
        'expiring_items': expiring,
    }
    return _truth_wrap('renewals', result, truth_class="DERIVED",
                      confidence=0.6,
                      evidence=[{"type": "state_file", "description": "Loaded from local state files"}],
                      limitations=["Renewals based on locally stored dates, not live API checks"])


# ============================================================
# VERIFICATION STATUS TOOL
# ============================================================

def verification_status(task_filter=None):
    """Show verification status of all tasks and workflow steps."""
    tasks_status = {}

    for tid, task in TASK_DB.items():
        if task_filter and task_filter not in tid:
            continue
        tasks_status[tid] = {
            'task_name': task.get('task_name', ''),
            'category': task.get('category', ''),
            'truth_class': task.get('truth_class', 'CONCEPTUAL'),
            'verified_at': task.get('verified_at'),
            'verification_method': task.get('verification_method', 'none'),
            'source_url': task.get('source_url', ''),
            'source_hash': task.get('source_hash'),
            'next_verification_due': task.get('next_verification_due'),
        }

    workflow_tools = ['move_house', 'manage_car', 'onboard_car', 'manage_business',
                      'change_details_everywhere', 'renew_passport', 'start_driving',
                      'start_regulated_business', 'resolve_letter', 'admin_audit', 'renewals']

    workflows_status = {}
    for tool_name in workflow_tools:
        workflows_status[tool_name] = {
            'truth_class': 'CONCEPTUAL',
            'verified_steps': 0,
            'total_steps': 'varies',
            'note': 'All steps currently NOT_VERIFIED — source URLs provided but not checked against live pages',
        }

    total_tasks = len(tasks_status)
    verified_tasks = sum(1 for t in tasks_status.values() if t['truth_class'] == 'VERIFIED')
    conceptual_tasks = sum(1 for t in tasks_status.values() if t['truth_class'] == 'CONCEPTUAL')

    result = {
        'status': 'ok',
        'summary': {
            'total_tasks': total_tasks,
            'verified_tasks': verified_tasks,
            'conceptual_tasks': conceptual_tasks,
            'derivation_date': DEFAULT_AS_OF,
            'next_verification_due': _default_next_verification(),
            'verification_period_days': VERIFICATION_PERIOD_DAYS,
        },
        'tasks': tasks_status,
        'workflows': workflows_status,
        'truth_class_definitions': TRUTH_CLASSES,
        'verification_methods': VERIFICATION_METHODS,
        'action': {
            'class': 'USER_HANDOFF',
            'note': 'To verify tasks: fetch each source_url, hash the content, compare with source_hash, update verified_at and truth_class',
        },
    }
    return _truth_wrap('verification_status', result, truth_class="VERIFIED",
                      confidence=1.0,
                      evidence=[{"type": "metadata", "description": "Verification status report generated from local task database"}],
                      limitations=[],
                      method_id="verification_audit",
                      method_version="1.0.0")


# ============================================================
# DISPATCH
# ============================================================

DISPATCH = {
    'explain_task': explain_task,
    'check_requirements': check_requirements,
    'can_agent_do_it': can_agent_do_it,
    'moving_house_checklist': moving_house_checklist,
    'start_sole_trader': start_sole_trader,
    'tax_obligations': tax_obligations,
    'new_parent_admin': new_parent_admin,
    'used_car_checks': used_car_checks,
    'lost_passport': lost_passport,
    'manage_mot': manage_mot,
    'support_check': support_check,
    'company_setup': company_setup,
    'move_house': move_house,
    'manage_car': manage_car,
    'onboard_car': onboard_car,
    'manage_business': manage_business,
    'change_details_everywhere': change_details_everywhere,
    'renew_passport': renew_passport,
    'start_driving': start_driving,
    'start_regulated_business': start_regulated_business,
    'resolve_letter': resolve_letter,
    'admin_audit': admin_audit,
    'renewals': renewals,
    'verification_status': verification_status,
}


def handle_tool_call(name, args):
    func = DISPATCH.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except TypeError as e:
        return {"error": f"Invalid args: {e}"}


# ============================================================
# MCP STDIO SERVER
# ============================================================

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
            response = {
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "uk_admin", "version": "3.0.0",
                                   "description": "UK Admin MCP - PR5 Truth Contract. Every response includes source verification metadata. Boring UK's value IS verification."},
                },
            }
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = msg.get("params", {})
            result = handle_tool_call(params.get("name", ""), params.get("arguments", {}))
            response = {"jsonrpc": "2.0", "id": msg_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}}
        else:
            response = {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}}

        print(json.dumps(response), flush=True)


if __name__ == '__main__':
    if '--serve' in sys.argv:
        run_mcp_stdio()
    elif len(sys.argv) > 2:
        result = handle_tool_call(sys.argv[1], json.loads(sys.argv[2]))
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps({"name": "uk_admin", "version": "3.0.0", "tools": [t["name"] for t in TOOLS]}, indent=2))
