#!/usr/bin/env python3
"""
UK Admin MCP Server - Get boring British things done.

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

Usage:
    python uk_admin_mcp.py                     # List tools
    python uk_admin_mcp.py <tool> '<json>'     # Call tool
    python uk_admin_mcp.py --serve             # MCP stdio server
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'uk_admin' / 'data'
sys.path.insert(0, str(ROOT))


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
# CURATED TASK DATABASE
# ============================================================

TASK_DB = {
    'renew_driving_licence': {
        'task_name': 'Renew your driving licence',
        'category': 'driving', 'subcategory': 'licence', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/renew-driving-licence',
        'cost_gbp': 14.00, 'takes_time': '3 weeks',
        'requires': ['identity', 'licence_details', 'address', 'photo'],
        'how_to': [
            '1. Go to https://www.gov.uk/renew-driving-licence',
            '2. You need your driving licence number, addresses for last 3 years, and a passport photo',
            '3. Pay 14.00 by card',
            '4. Your new licence arrives in about 3 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'failure_modes': ['identity_mismatch', 'address_mismatch'],
        'is_recurring': True, 'recurrence': 'every 10 years',
        'related_tasks': ['update_address', 'replace_lost_licence'],
    },
    'replace_lost_licence': {
        'task_name': 'Replace a lost or stolen driving licence',
        'category': 'driving', 'subcategory': 'licence', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/replace-driving-licence',
        'cost_gbp': 20.00, 'takes_time': '3 weeks',
        'requires': ['identity', 'address', 'photo', 'lost_or_stolen_declaration'],
        'how_to': [
            '1. If stolen, report to police first',
            '2. Go to https://www.gov.uk/replace-driving-licence',
            '3. You need your driving licence number or personal details',
            '4. Pay 20.00',
            '5. New licence arrives in about 3 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['renew_driving_licence'],
    },
    'update_address': {
        'task_name': 'Change the address on your driving licence',
        'category': 'driving', 'subcategory': 'licence', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/change-address-driving-licence',
        'cost_gbp': 0.00, 'takes_time': '3 weeks',
        'requires': ['identity', 'new_address', 'old_address'],
        'how_to': [
            '1. Go to https://www.gov.uk/change-address-driving-licence',
            '2. Enter your driving licence number and new address',
            '3. Free - no payment needed',
            '4. Updated licence arrives in about 3 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['renew_driving_licence', 'update_vehicle_tax'],
    },
    'view_licence_points': {
        'task_name': 'Check your driving licence information',
        'category': 'driving', 'subcategory': 'licence', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/view-driving-licence',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['driving_licence_number', 'national_insurance_number'],
        'how_to': [
            '1. Go to https://www.gov.uk/view-driving-licence',
            '2. Enter your driving licence number and National Insurance number',
            '3. View endorsements, restrictions, and expiry dates',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible',
        },
    },
    'check_mot': {
        'task_name': 'Check MOT history of a vehicle',
        'category': 'vehicle', 'subcategory': 'mot', 'authority': 'DVSA',
        'url': 'https://www.gov.uk/check-mot-history',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'how_to': [
            '1. Go to https://www.gov.uk/check-mot-history',
            '2. Enter the vehicle registration number',
            '3. See MOT history, advisories, and expiry date',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['book_mot', 'check_vehicle_tax'],
    },
    'book_mot': {
        'task_name': 'Book an MOT',
        'category': 'vehicle', 'subcategory': 'mot', 'authority': 'DVSA',
        'url': 'https://www.gov.uk/get-mot',
        'cost_gbp': 54.85, 'takes_time': '1 hour',
        'requires': ['vehicle_registration'],
        'how_to': [
            '1. Go to https://www.gov.uk/get-mot',
            '2. Enter your registration number',
            '3. Find a local garage - prices vary (max 54.85 for cars)',
            '4. Book online or by phone',
            '5. Take your vehicle on the booked date',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'every 12 months',
        'related_tasks': ['check_mot', 'check_vehicle_tax'],
    },
    'check_vehicle_tax': {
        'task_name': 'Check vehicle tax',
        'category': 'vehicle', 'subcategory': 'tax', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/check-vehicle-tax',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'how_to': [
            '1. Go to https://www.gov.uk/check-vehicle-tax',
            '2. Enter the vehicle registration number',
            '3. See tax status, expiry date, and MOT expiry',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_vehicle_tax', 'check_mot'],
    },
    'update_vehicle_tax': {
        'task_name': 'Tax your vehicle',
        'category': 'vehicle', 'subcategory': 'tax', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/vehicle-tax',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['vehicle_registration', 'insurance', 'mot_certificate'],
        'how_to': [
            '1. Go to https://www.gov.uk/vehicle-tax',
            '2. Enter registration number',
            '3. You need a valid MOT and insurance',
            '4. Pay by card - cost depends on vehicle',
            '5. Tax is instant from the start date',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'every 6 or 12 months',
        'related_tasks': ['check_vehicle_tax', 'book_mot'],
    },
    'sorn_vehicle': {
        'task_name': 'Declare a vehicle off the road (SORN)',
        'category': 'vehicle', 'subcategory': 'tax', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/sorn-statutory-off-road-notification',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'how_to': [
            '1. Go to https://www.gov.uk/sorn-statutory-off-road-notification',
            '2. Enter registration and details',
            '3. Free to declare',
            '4. Vehicle must be kept off public roads',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_vehicle_tax'],
    },
    'transfer_vehicle': {
        'task_name': 'Sell or transfer a vehicle',
        'category': 'vehicle', 'subcategory': 'ownership', 'authority': 'DVLA',
        'url': 'https://www.gov.uk/sold-bought-vehicle',
        'cost_gbp': 0.00, 'takes_time': '1-5 days',
        'requires': ['vehicle_registration', 'new_keeper_details', 'v5c'],
        'how_to': [
            '1. Fill in section 6 of the V5C (keep section 9)',
            '2. Give section 9 to the new keeper',
            '3. Send section 6 to DVLA or do it online',
            '4. Notify your insurer',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_vehicle_tax', 'sorn_vehicle'],
    },
    'apply_passport': {
        'task_name': 'Apply for a UK passport',
        'category': 'passport', 'subcategory': 'application', 'authority': 'HM Passport Office',
        'url': 'https://www.gov.uk/apply-renew-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'birth_certificate', 'countersignatory'],
        'how_to': [
            '1. Go to https://www.gov.uk/apply-renew-passport',
            '2. You need a digital photo and someone to countersign',
            '3. Fill in the online form',
            '4. Pay 82.50 (or 92.50 for post office check and send)',
            '5. Post your old documents if required',
            '6. Passport arrives in about 10 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['renew_passport', 'replace_lost_passport'],
    },
    'renew_passport': {
        'task_name': 'Renew your passport',
        'category': 'passport', 'subcategory': 'renewal', 'authority': 'HM Passport Office',
        'url': 'https://www.gov.uk/renew-adult-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'existing_passport'],
        'how_to': [
            '1. Go to https://www.gov.uk/renew-adult-passport',
            '2. You need your current passport and a new digital photo',
            '3. Fill in online form - some questions from your old passport',
            '4. Pay 82.50',
            '5. Post your old passport back',
            '6. New passport arrives in about 10 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'every 10 years',
        'related_tasks': ['apply_passport'],
    },
    'replace_lost_passport': {
        'task_name': 'Replace a lost or stolen passport',
        'category': 'passport', 'subcategory': 'replacement', 'authority': 'HM Passport Office',
        'url': 'https://www.gov.uk/replace-lost-stolen-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'lost_or_stolen_declaration'],
        'how_to': [
            '1. Report it lost or stolen: https://www.gov.uk/report-a-lost-or-stolen-passport',
            '2. Then apply for a replacement: https://www.gov.uk/replace-lost-stolen-passport',
            '3. You need a new photo and may need a countersignatory',
            '4. Pay 82.50',
            '5. Your old passport is cancelled immediately',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['renew_passport'],
    },
    'report_passport_lost': {
        'task_name': 'Report a lost or stolen passport',
        'category': 'passport', 'subcategory': 'security', 'authority': 'HM Passport Office',
        'url': 'https://www.gov.uk/report-a-lost-or-stolen-passport',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['passport_number', 'personal_details'],
        'how_to': [
            '1. Go to https://www.gov.uk/report-a-lost-or-stolen-passport',
            '2. Enter your passport number and personal details',
            '3. Your passport is cancelled immediately',
            '4. You can then apply for a replacement',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['replace_lost_passport'],
    },
    'self_assessment_register': {
        'task_name': 'Register for Self Assessment',
        'category': 'tax', 'subcategory': 'self_assessment', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/register-for-self-assessment',
        'cost_gbp': 0.00, 'takes_time': '10 working days',
        'requires': ['identity', 'national_insurance_number', 'employment_history'],
        'how_to': [
            '1. Go to https://www.gov.uk/register-for-self-assessment',
            '2. You need a Government Gateway account',
            '3. Enter your NI number and personal details',
            '4. HMRC sends you a UTR (Unique Taxpayer Reference)',
            '5. Use your UTR to file returns',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['self_assessment_submit'],
    },
    'self_assessment_submit': {
        'task_name': 'Complete your Self Assessment tax return',
        'category': 'tax', 'subcategory': 'self_assessment', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/self-assessment-tax-returns',
        'cost_gbp': 0.00, 'takes_time': '1-3 hours',
        'requires': ['identity', 'national_insurance_number', 'income_details', 'expenses'],
        'how_to': [
            '1. Log in to Government Gateway',
            '2. Go to Self Assessment and fill in the return',
            '3. You need P60, P11D, bank statements, expense receipts',
            '4. File online by 31 January',
            '5. Pay any tax owed',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'annually by 31 January',
        'related_tasks': ['self_assessment_register', 'pay_tax_bill'],
    },
    'pay_tax_bill': {
        'task_name': 'Pay your Self Assessment tax bill',
        'category': 'tax', 'subcategory': 'payment', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/pay-self-assessment-tax-bill',
        'cost_gbp': 0.00, 'takes_time': 'instant to 5 working days',
        'requires': ['identity', 'tax_reference', 'payment_method'],
        'how_to': [
            '1. Go to https://www.gov.uk/pay-self-assessment-tax-bill',
            '2. Log in with your Government Gateway account',
            '3. Pay by card, bank transfer, or direct debit',
            '4. On account payments due 31 July',
            '5. Balance payment due 31 January',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['self_assessment_submit'],
    },
    'check_tax_code': {
        'task_name': 'Check your tax code',
        'category': 'tax', 'subcategory': 'employment', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/check-income-tax-returns',
        'cost_gbp': 0.00, 'takes_time': 'instant',
        'requires': ['identity', 'national_insurance_number'],
        'how_to': [
            '1. Log in to your Personal Tax Account',
            '2. Go to Income Tax to see your tax code',
            '3. Your tax code tells your employer how much tax to deduct',
            '4. Contact HMRC if it looks wrong',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['self_assessment_register'],
    },
    'claim_tax_refund': {
        'task_name': 'Claim a tax refund',
        'category': 'tax', 'subcategory': 'refund', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/claim-tax-refund',
        'cost_gbp': 0.00, 'takes_time': '6 weeks',
        'requires': ['identity', 'p60', 'p45', 'bank_details'],
        'how_to': [
            '1. Go to https://www.gov.uk/claim-tax-refund',
            '2. Log in to your Personal Tax Account',
            '3. Follow the refund claim process',
            '4. You need your P60 or P45',
            '5. Refund is paid into your bank account',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['check_tax_code'],
    },
    'setup_sole_trader': {
        'task_name': 'Set up as a sole trader',
        'category': 'business', 'subcategory': 'self_employment', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/working-for-yourself',
        'cost_gbp': 0.00, 'takes_time': '10 working days for UTR',
        'requires': ['identity', 'national_insurance_number', 'business_details'],
        'how_to': [
            '1. Register as self-employed with HMRC',
            '2. Go to https://www.gov.uk/working-for-yourself',
            '3. You need a Government Gateway account',
            '4. HMRC sends you a UTR (Unique Taxpayer Reference)',
            '5. Keep records of income and expenses',
            '6. File a Self Assessment tax return each year',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['self_assessment_register', 'register_for_vat'],
    },
    'register_limited_company': {
        'task_name': 'Register a limited company',
        'category': 'business', 'subcategory': 'company_formation', 'authority': 'Companies House',
        'url': 'https://www.gov.uk/limited-company-formation',
        'cost_gbp': 12.00, 'takes_time': '24 hours',
        'requires': ['identity', 'registered_address', 'directors', 'articles_of_association'],
        'how_to': [
            '1. Go to https://www.gov.uk/limited-company-formation',
            '2. Choose a company name (check availability)',
            '3. Provide registered office address',
            '4. Appoint at least one director',
            '5. Create articles of association',
            '6. Register online for 12 or by post for 40',
            '7. Company is typically registered within 24 hours',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['register_corporation_tax', 'register_for_vat'],
    },
    'register_for_vat': {
        'task_name': 'Register for VAT',
        'category': 'business', 'subcategory': 'vat', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/register-for-vat',
        'cost_gbp': 0.00, 'takes_time': '14 working days',
        'requires': ['identity', 'business_details'],
        'how_to': [
            '1. Go to https://www.gov.uk/register-for-vat',
            '2. You must register if turnover exceeds 85,000',
            '3. Log in with Government Gateway',
            '4. Enter business details and expected turnover',
            '5. You receive a VAT number in about 2 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['submit_vat_return'],
    },
    'submit_vat_return': {
        'task_name': 'Submit a VAT return',
        'category': 'business', 'subcategory': 'vat', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/vat-returns',
        'cost_gbp': 0.00, 'takes_time': '30 minutes',
        'requires': ['identity', 'vat_number', 'turnover_data'],
        'how_to': [
            '1. Log in to Government Gateway',
            '2. Go to your VAT account',
            '3. Enter sales and purchase figures for the quarter',
            '4. File by the deadline (1 month and 7 days after quarter end)',
            '5. Pay any VAT owed',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'quarterly',
        'related_tasks': ['register_for_vat'],
    },
    'register_corporation_tax': {
        'task_name': 'Register for Corporation Tax',
        'category': 'business', 'subcategory': 'corporation_tax', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/register-for-corporation-tax',
        'cost_gbp': 0.00, 'takes_time': '15 working days',
        'requires': ['company_number', 'company_name'],
        'how_to': [
            '1. Go to https://www.gov.uk/register-for-corporation-tax',
            '2. Enter your company number and Corporation Tax reference',
            '3. HMRC sends you an activation code',
            '4. Activate your account to manage online',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['pay_corporation_tax', 'register_limited_company'],
    },
    'pay_corporation_tax': {
        'task_name': 'Pay Corporation Tax',
        'category': 'business', 'subcategory': 'corporation_tax', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/pay-corporation-tax',
        'cost_gbp': 0.00, 'takes_time': 'instant to 5 working days',
        'requires': ['company_number', 'payment_method'],
        'how_to': [
            '1. Go to https://www.gov.uk/pay-corporation-tax',
            '2. Log in with your Corporation Tax account',
            '3. Pay by bank transfer, card, or direct debit',
            '4. Payment must reach HMRC by the deadline',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['submit_corporation_tax_return'],
    },
    'submit_corporation_tax_return': {
        'task_name': 'File a Company Tax Return',
        'category': 'business', 'subcategory': 'corporation_tax', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/file-company-tax-return',
        'cost_gbp': 0.00, 'takes_time': '1-3 hours',
        'requires': ['company_number', 'accounts', 'tax_computation'],
        'how_to': [
            '1. Go to https://www.gov.uk/file-company-tax-return',
            '2. Log in with your Corporation Tax account',
            '3. Upload your company accounts',
            '4. Complete the tax computation',
            '5. File within 12 months of your accounting period end',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval',
        },
        'is_recurring': True, 'recurrence': 'annually',
        'related_tasks': ['pay_corporation_tax'],
    },
    'update_council_tax': {
        'task_name': 'Update your council tax details',
        'category': 'home', 'subcategory': 'council_tax', 'authority': 'Local Council',
        'url': 'https://www.gov.uk/council-tax',
        'cost_gbp': 0.00, 'takes_time': 'varies',
        'requires': ['identity', 'address', 'move_date'],
        'how_to': [
            '1. Find your council: https://www.gov.uk/find-local-council',
            '2. Contact them to update your address or band',
            '3. If moving, notify both old and new councils',
            '4. You may be eligible for a single person discount',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_electoral_roll', 'update_vehicle_tax'],
    },
    'update_electoral_roll': {
        'task_name': 'Register to vote',
        'category': 'home', 'subcategory': 'electoral', 'authority': 'Electoral Commission',
        'url': 'https://www.gov.uk/register-to-vote',
        'cost_gbp': 0.00, 'takes_time': '2 weeks',
        'requires': ['identity', 'address', 'nationality'],
        'how_to': [
            '1. Go to https://www.gov.uk/register-to-vote',
            '2. Enter your name, address, and National Insurance number',
            '3. Registration takes about 2 weeks',
            '4. You need to re-register when you move',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_council_tax'],
    },
    'moving_house_checklist': {
        'task_name': 'Update everything when you move house',
        'category': 'home', 'subcategory': 'moving', 'authority': 'Multiple',
        'url': 'https://www.gov.uk/medical-records/notifying-people',
        'cost_gbp': 0.00, 'takes_time': '1-2 weeks',
        'requires': ['old_address', 'new_address', 'move_date'],
        'how_to': [
            '1. Notify your council for council tax',
            '2. Update your driving licence (DVLA)',
            '3. Update your vehicle tax (DVLA)',
            '4. Register to vote at new address',
            '5. Notify your bank and credit cards',
            '6. Redirect your post: https://www.royalmail.com/redirection',
            '7. Notify utility providers',
            '8. Update insurance policies',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['update_address', 'update_council_tax', 'update_electoral_roll'],
    },
    'new_baby_admin': {
        'task_name': 'Register a birth and claim child benefits',
        'category': 'family', 'subcategory': 'new_parent', 'authority': 'Multiple',
        'url': 'https://www.gov.uk/child-birth-registration',
        'cost_gbp': 11.00, 'takes_time': '42 days to register',
        'requires': ['identity', 'baby_details', 'parents_details', 'address'],
        'how_to': [
            '1. Register the birth within 42 days at your local register office',
            '2. Fee is 11.00 for a standard certificate',
            '3. You get the birth certificate and a NHS number',
            '4. Apply for Child Benefit: https://www.gov.uk/child-benefit',
            '5. Update council tax (you may get a discount)',
            '6. Notify your employer (maternity/paternity pay)',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval',
        },
        'related_tasks': ['apply_child_benefit', 'update_council_tax'],
    },
    'apply_child_benefit': {
        'task_name': 'Apply for Child Benefit',
        'category': 'benefits', 'subcategory': 'child_benefit', 'authority': 'HMRC',
        'url': 'https://www.gov.uk/child-benefit',
        'cost_gbp': 0.00, 'takes_time': '6-8 weeks',
        'requires': ['identity', 'baby_birth_certificate', 'national_insurance_number'],
        'how_to': [
            '1. Go to https://www.gov.uk/child-benefit',
            '2. Fill in form CH2',
            '3. Send with the birth certificate',
            '4. Payments start in about 6-8 weeks',
            '5. High Income Charge may apply if either parent earns over 60k',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['new_baby_admin'],
    },
    'check_benefits': {
        'task_name': 'Check what benefits you can get',
        'category': 'benefits', 'subcategory': 'eligibility', 'authority': 'DWP',
        'url': 'https://www.gov.uk/browse/child-disability-family/benefits',
        'cost_gbp': 0.00, 'takes_time': '5 minutes',
        'requires': ['identity', 'income_details', 'household_details'],
        'how_to': [
            '1. Use the benefits calculator: https://www.gov.uk/benefits-calculators',
            '2. Enter your income, savings, and household details',
            '3. See what you might be eligible for',
            '4. Common benefits: Universal Credit, Child Benefit, PIP, Council Tax Reduction',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['apply_universal_credit', 'apply_pip'],
    },
    'apply_universal_credit': {
        'task_name': 'Apply for Universal Credit',
        'category': 'benefits', 'subcategory': 'universal_credit', 'authority': 'DWP',
        'url': 'https://www.gov.uk/universal-credit/how-to-apply',
        'cost_gbp': 0.00, 'takes_time': '5-8 weeks for first payment',
        'requires': ['identity', 'income_details', 'housing_costs', 'bank_details'],
        'how_to': [
            '1. Go to https://www.gov.uk/universal-credit/how-to-apply',
            '2. You need a Government Gateway account and a bank account',
            '3. You must apply as a couple if you live together',
            '4. Attend a Jobcentre Plus appointment',
            '5. First payment takes at least 5 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['check_benefits', 'apply_pip'],
    },
    'apply_pip': {
        'task_name': 'Apply for Personal Independence Payment',
        'category': 'benefits', 'subcategory': 'disability', 'authority': 'DWP',
        'url': 'https://www.gov.uk/pip/how-to-apply',
        'cost_gbp': 0.00, 'takes_time': '8-12 weeks',
        'requires': ['identity', 'health_conditions', 'care_needs'],
        'how_to': [
            '1. Call the PIP new claims line: 0800 917 2222',
            '2. You cannot apply online',
            '3. Fill in the PIP2 evidence form',
            '4. Attend a face-to-face or phone assessment',
            '5. Decision takes about 8-12 weeks',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible',
        },
        'related_tasks': ['check_benefits', 'apply_universal_credit'],
    },
    'check_employment_rights': {
        'task_name': 'Check your employment rights',
        'category': 'employment', 'subcategory': 'rights', 'authority': 'ACAS',
        'url': 'https://www.gov.uk/employment-rights-for-employees',
        'cost_gbp': 0.00, 'takes_time': '5 minutes',
        'requires': [],
        'how_to': [
            '1. Go to https://www.gov.uk/employment-rights-for-employees',
            '2. Browse rights by topic: pay, holidays, redundancy, dismissal',
            '3. Check your contract and employer policies',
            '4. For disputes, contact ACAS: https://www.acas.org.uk',
        ],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible',
        },
    },
}


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
    # ---- NEW BORING UK WORKFLOW TOOLS (12) ----
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
]


# ============================================================
# IMPLEMENTATIONS (original 12)
# ============================================================

def _find_task(query):
    q = query.lower().strip()
    if q in TASK_DB:
        return TASK_DB[q]
    for tid, task in TASK_DB.items():
        if q.replace(' ', '_') == tid:
            return task
    for tid, task in TASK_DB.items():
        if q in task['task_name'].lower():
            return task
    keywords = q.split()
    for tid, task in TASK_DB.items():
        words = task['task_name'].lower().split()
        if any(kw in words for kw in keywords):
            return task
    return None


def explain_task(task):
    td = _find_task(task)
    if not td:
        available = {}
        for tid, t in TASK_DB.items():
            available.setdefault(t['category'], []).append(tid)
        return {'status': 'not_found', 'query': task, 'available_tasks': available}
    return {
        'status': 'ok',
        'task': td['task_name'],
        'category': td['category'],
        'authority': td['authority'],
        'url': td['url'],
        'cost': f"\u00a3{td['cost_gbp']:.2f}" if td['cost_gbp'] else 'Free',
        'time': td.get('takes_time', 'Unknown'),
        'steps': td.get('how_to', []),
        'related_tasks': td.get('related_tasks', []),
        'recurring': td.get('is_recurring', False),
        'recurrence': td.get('recurrence', ''),
    }


def check_requirements(task):
    td = _find_task(task)
    if not td:
        return {'status': 'not_found', 'query': task}
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
    return {
        'status': 'ok',
        'task': td['task_name'],
        'url': td['url'],
        'requirements': checklist,
        'count': len(reqs),
    }


def can_agent_do_it(task):
    td = _find_task(task)
    if not td:
        return {'status': 'not_found', 'query': task}
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
    return {
        'status': 'ok',
        'task': td['task_name'],
        'agent_can_do': what_agent_can,
        'user_must_do': what_user_must,
        'permissions': perms,
        'verdict': 'FULLY_ASSISTED' if perms.get('submit') and payment != 'not_possible' else 'ASSISTED_WITH_APPROVAL' if perms.get('prefill') else 'GUIDANCE_ONLY',
    }


def moving_house_checklist(new_address, move_date, old_address=''):
    items = [
        {'task': 'update_address', 'what': 'Update driving licence address', 'authority': 'DVLA', 'cost': 'Free', 'deadline': 'Within 8 weeks', 'url': 'https://www.gov.uk/change-address-driving-licence'},
        {'task': 'update_vehicle_tax', 'what': 'Update vehicle tax address', 'authority': 'DVLA', 'cost': 'Free', 'deadline': 'Immediately', 'url': 'https://www.gov.uk/vehicle-tax'},
        {'task': 'update_council_tax', 'what': 'Notify council for council tax', 'authority': 'Local Council', 'cost': 'Free', 'deadline': 'On or before move date', 'url': 'https://www.gov.uk/council-tax'},
        {'task': 'update_electoral_roll', 'what': 'Register to vote at new address', 'authority': 'Electoral Commission', 'cost': 'Free', 'deadline': '12 working days before election', 'url': 'https://www.gov.uk/register-to-vote'},
        {'task': 'redirect_post', 'what': 'Redirect your post', 'authority': 'Royal Mail', 'cost': 'From 82.99', 'deadline': 'Before you move', 'url': 'https://www.royalmail.com/redirection'},
        {'task': 'update_banks', 'what': 'Update bank and credit card addresses', 'authority': 'Banks', 'cost': 'Free', 'deadline': 'Within a few weeks', 'url': ''},
        {'task': 'update_utilities', 'what': 'Notify gas, electric, water, council', 'authority': 'Utility providers', 'cost': 'Free', 'deadline': 'Before you move', 'url': ''},
        {'task': 'update_insurance', 'what': 'Update home, car, and other insurance', 'authority': 'Insurers', 'cost': 'Free', 'deadline': 'Before you move', 'url': ''},
    ]
    return {
        'status': 'ok',
        'new_address': new_address,
        'old_address': old_address,
        'move_date': move_date,
        'checklist': items,
        'count': len(items),
        'tip': 'Start with DVLA and council tax - they have legal deadlines.',
    }


def start_sole_trader(business_name='', business_type=''):
    td = TASK_DB['setup_sole_trader']
    return {
        'status': 'ok',
        'task': 'Set up as a sole trader',
        'business_name': business_name,
        'business_type': business_type,
        'steps': td['how_to'],
        'cost': 'Free',
        'time': '10 working days for UTR',
        'url': td['url'],
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
    }


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
    return {
        'status': 'ok',
        'situation': situation,
        'obligations': obligations,
        'tip': 'Log in to your Personal Tax Account to see exactly what HMRC expects from you.',
        'url': 'https://www.gov.uk/log-in-register-hmrc-online-services',
    }


def new_parent_admin():
    return {
        'status': 'ok',
        'checklist': [
            {'step': 'Register the birth', 'deadline': 'Within 42 days', 'cost': '11.00', 'where': 'Local register office'},
            {'step': 'Apply for Child Benefit', 'deadline': 'As soon as possible', 'cost': 'Free', 'where': 'HMRC'},
            {'step': 'Update council tax', 'deadline': 'Before the birth', 'cost': 'Free', 'where': 'Your council'},
            {'step': 'Notify your employer', 'deadline': '15 weeks before due date', 'cost': 'Free', 'where': 'Your employer'},
            {'step': 'Check tax code', 'deadline': 'After birth', 'cost': 'Free', 'where': 'HMRC'},
        ],
        'tip': 'Register the birth first - you need the birth certificate for everything else.',
    }


def used_car_checks(registration, make='', model=''):
    return {
        'status': 'ok',
        'registration': registration,
        'make': make,
        'model': model,
        'checks': [
            {'check': 'MOT history', 'what': 'Passes, failures, advisories', 'url': 'https://www.gov.uk/check-mot-history', 'free': True},
            {'check': 'Vehicle tax', 'what': 'Current tax status and expiry', 'url': 'https://www.gov.uk/check-vehicle-tax', 'free': True},
            {'check': 'Recall check', 'what': 'Outstanding safety recalls', 'url': 'https://www.gov.uk/check-vehicle-recalls', 'free': True},
            {'check': 'Insurance group', 'what': 'How expensive to insure', 'url': 'https://www.motorway.co.uk/guides/insurance-groups-explained', 'free': True},
            {'check': 'HPI check', 'what': 'Finance, written off, stolen', 'url': 'https://www.checkcardetails.co.uk/', 'free': False},
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


def lost_passport(was_stolen=False):
    return {
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


def manage_mot(registration):
    return {
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


def support_check(situation):
    sit = situation.lower()
    benefits = []
    if any(w in sit for w in ['kid', 'child', 'baby', 'family', 'parent']):
        benefits.append({'benefit': 'Child Benefit', 'amount': '25.60/week (eldest)', 'url': 'https://www.gov.uk/child-benefit'})
    if any(w in sit for w in ['unemploy', 'jobseek', 'looking for work']):
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Up to 393.45/month (under 25)', 'url': 'https://www.gov.uk/universal-credit'})
    if any(w in sit for w in ['disabled', 'disability', 'ill', 'mental health', 'mobility']):
        benefits.append({'benefit': 'PIP', 'amount': '72.65-184.25/week', 'url': 'https://www.gov.uk/pip'})
        benefits.append({'benefit': 'Employment and Support Allowance', 'amount': '84.80/week', 'url': 'https://www.gov.uk/employment-and-support-allowance'})
    if any(w in sit for w in ['low income', 'struggling', 'rent', 'housing']):
        benefits.append({'benefit': 'Universal Credit (housing element)', 'amount': 'Varies by area', 'url': 'https://www.gov.uk/universal-credit'})
        benefits.append({'benefit': 'Council Tax Reduction', 'amount': 'Up to 100%', 'url': 'https://www.gov.uk/council-tax-reduction'})
    if any(w in sit for w in ['carer', 'looking after']):
        benefits.append({'benefit': "Carer's Allowance", 'amount': '81.90/week', 'url': 'https://www.gov.uk/carers-allowance'})
    if not benefits:
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Varies', 'url': 'https://www.gov.uk/universal-credit'})
    return {
        'status': 'ok',
        'situation': situation,
        'possible_benefits': benefits,
        'calculator': 'https://www.gov.uk/benefits-calculators',
    }


def company_setup(company_name='', sector=''):
    return {
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


# ============================================================
# BORING UK WORKFLOW IMPLEMENTATIONS (12 new tools)
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
        {
            'step': 1, 'task': 'Notify current council',
            'what': 'Tell your old council you are leaving',
            'deadline': _days_before(14),
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/council-tax',
            'authority': 'Old council',
            'dependency': None,
            'note': 'Council tax is a legal obligation. Contact both old and new councils.',
        },
        {
            'step': 2, 'task': 'Notify new council',
            'what': 'Set up council tax at new address',
            'deadline': move_date,
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/find-local-council',
            'authority': 'New council',
            'dependency': 'step_1',
        },
        {
            'step': 3, 'task': 'Update driving licence',
            'what': 'Change address on DVLA driving licence',
            'deadline': _days_before(0),
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/change-address-driving-licence',
            'authority': 'DVLA',
            'deadline_legal': 'Within 8 weeks of moving',
            'dependency': None,
            'fee': 'Free',
        },
        {
            'step': 4, 'task': 'Update vehicle tax',
            'what': 'Update address on vehicle tax records',
            'deadline': _days_before(0),
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/vehicle-tax',
            'authority': 'DVLA',
            'dependency': 'step_3',
            'fee': 'Free',
        },
        {
            'step': 5, 'task': 'Register to vote at new address',
            'what': 'Register on the electoral roll',
            'deadline': _days_before(12),
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/register-to-vote',
            'authority': 'Electoral Commission',
            'dependency': None,
        },
        {
            'step': 6, 'task': 'Redirect post via Royal Mail',
            'what': 'Set up mail redirection',
            'deadline': _days_before(5),
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.royalmail.com/redirection',
            'authority': 'Royal Mail',
            'dependency': None,
            'fee': 'From 82.99 for 12 months',
        },
        {
            'step': 7, 'task': 'Notify banks and credit cards',
            'what': 'Update address on all bank accounts',
            'deadline': _days_before(-7),
            'action_class': 'USER_HANDOFF',
            'authority': 'Your banks',
            'dependency': None,
            'note': 'Update each bank separately.',
        },
        {
            'step': 8, 'task': 'Notify utility providers',
            'what': 'Gas, electric, water, broadband, TV licence',
            'deadline': _days_before(7),
            'action_class': 'USER_HANDOFF',
            'authority': 'Utility providers',
            'dependency': None,
            'note': 'Take meter readings on move day.',
        },
        {
            'step': 9, 'task': 'Update insurance policies',
            'what': 'Home, car, and other insurance',
            'deadline': _days_before(0),
            'action_class': 'USER_HANDOFF',
            'authority': 'Insurers',
            'dependency': None,
            'note': 'Car insurance must reflect new address.',
        },
        {
            'step': 10, 'task': 'Notify employer',
            'what': 'Update payroll and HR',
            'deadline': _days_before(7),
            'action_class': 'USER_HANDOFF',
            'authority': 'Your employer',
            'dependency': None,
        },
        {
            'step': 11, 'task': 'Notify GP and dentist',
            'what': 'Register at new local surgeries',
            'deadline': _days_before(-14),
            'action_class': 'USER_HANDOFF',
            'authority': 'NHS',
            'dependency': None,
        },
        {
            'step': 12, 'task': 'Notify HMRC of address change',
            'what': 'Update personal tax account',
            'deadline': _days_before(0),
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/update-hmrc-your-personal-details',
            'authority': 'HMRC',
            'dependency': None,
        },
    ]

    return {
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
        'official_urls': [
            'https://www.gov.uk/change-address-driving-licence',
            'https://www.gov.uk/vehicle-tax',
            'https://www.gov.uk/find-local-council',
            'https://www.gov.uk/register-to-vote',
            'https://www.royalmail.com/redirection',
            'https://www.gov.uk/update-hmrc-your-personal-details',
        ],
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
    }


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
            'url': 'https://www.gov.uk/get-mot',
        })
    else:
        renewals.append({
            'item': 'MOT',
            'expiry': 'Unknown',
            'action_class': 'APPROVAL_REQUIRED',
            'urgent': False,
            'url': 'https://www.gov.uk/check-mot-history',
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
            'url': 'https://www.gov.uk/vehicle-tax',
        })
    else:
        renewals.append({
            'item': 'Road tax',
            'expiry': 'Unknown',
            'action_class': 'APPROVAL_REQUIRED',
            'urgent': False,
            'url': 'https://www.gov.uk/check-vehicle-tax',
        })

    return {
        'status': 'ok',
        'task': f'Manage car {registration}',
        'capability_level': 4,
        'workflow_steps': [
            {'step': 1, 'task': 'Check MOT status', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-mot-history'},
            {'step': 2, 'task': 'Check vehicle tax status', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-vehicle-tax'},
            {'step': 3, 'task': 'Check for recalls', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-vehicle-recalls'},
            {'step': 4, 'task': 'Verify insurance is current', 'action_class': 'USER_HANDOFF'},
            {'step': 5, 'task': 'Check V5C is correct', 'action_class': 'USER_HANDOFF'},
        ],
        'agent_actions': ['Check MOT history', 'Check tax status', 'Check recalls', 'Set renewal reminders'],
        'user_actions': ['Book MOT appointment', 'Arrange insurance', 'Keep V5C up to date', 'Fix any advisories'],
        'required_documents': ['V5C registration certificate', 'MOT certificate', 'Insurance certificate'],
        'deadlines': [
            f'MOT expiry: {car.get("mot_expiry", "unknown")}',
            f'Tax expiry: {car.get("tax_expiry", "unknown")}',
        ],
        'fees': ['MOT: max 54.85 (cars)', 'Road tax: varies by vehicle'],
        'official_urls': [
            'https://www.gov.uk/check-mot-history',
            'https://www.gov.uk/check-vehicle-tax',
            'https://www.gov.uk/check-vehicle-recalls',
            'https://www.gov.uk/get-mot',
            'https://www.gov.uk/vehicle-tax',
        ],
        'failure_modes': [
            'Driving without valid MOT (fine up to 2,500, 3 penalty points)',
            'Driving without road tax (fine up to 5,000, vehicle clamped)',
            'Ignoring recalls (safety risk)',
            'Insurance invalidated by vehicle changes',
        ],
        'follow_up_dates': renewals,
        'current_state': car,
    }


def onboard_car(registration):
    workflow_steps = [
        {
            'step': 1, 'task': 'Check MOT history',
            'what': 'Verify the car has a valid MOT and check history',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/check-mot-history',
            'fee': 'Free',
        },
        {
            'step': 2, 'task': 'Check vehicle tax',
            'what': 'Verify tax status and expiry',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/check-vehicle-tax',
            'fee': 'Free',
        },
        {
            'step': 3, 'task': 'Check for safety recalls',
            'what': 'Verify no outstanding recalls',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/check-vehicle-recalls',
            'fee': 'Free',
        },
        {
            'step': 4, 'task': 'Transfer V5C registration',
            'what': 'Complete section 6 and send to DVLA',
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/sold-bought-vehicle',
            'fee': 'Free',
            'deadline': 'As soon as possible',
        },
        {
            'step': 5, 'task': 'Get insurance',
            'what': 'Insure the car before driving',
            'action_class': 'USER_HANDOFF',
            'fee': 'Varies',
            'deadline': 'Before driving the car',
        },
        {
            'step': 6, 'task': 'Tax the vehicle',
            'what': 'Register for road tax with V5C and insurance',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/vehicle-tax',
            'fee': 'Varies',
            'dependency': 'step_4 and step_5',
        },
        {
            'step': 7, 'task': 'Get an MOT (if needed)',
            'what': 'If MOT has expired or is short',
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/get-mot',
            'fee': 'Up to 54.85',
        },
        {
            'step': 8, 'task': 'Update your insurance address',
            'what': 'If you have existing cover, update details',
            'action_class': 'USER_HANDOFF',
        },
        {
            'step': 9, 'task': 'Keep all documents safe',
            'what': 'V5C, MOT certificate, insurance certificate',
            'action_class': 'USER_HANDOFF',
        },
    ]

    return {
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
        'official_urls': [
            'https://www.gov.uk/check-mot-history',
            'https://www.gov.uk/check-vehicle-tax',
            'https://www.gov.uk/check-vehicle-recalls',
            'https://www.gov.uk/sold-bought-vehicle',
            'https://www.gov.uk/vehicle-tax',
            'https://www.gov.uk/get-mot',
        ],
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
    }


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
            'url': 'https://www.gov.uk/file-confirmation-statement',
            'fee': '13 online',
            'penalty': 'Company can be struck off',
        })
    if company.get('accounts_due'):
        deadlines.append({
            'filing': 'Annual Accounts',
            'deadline': company['accounts_due'],
            'authority': 'Companies House',
            'url': 'https://www.gov.uk/file-company-accounts',
            'fee': 'Free',
            'penalty': 'Up to 7,500 for private company',
        })
    if company.get('corporation_tax_due'):
        deadlines.append({
            'filing': 'Corporation Tax Return',
            'deadline': company['corporation_tax_due'],
            'authority': 'HMRC',
            'url': 'https://www.gov.uk/file-company-tax-return',
            'fee': 'Free',
            'penalty': 'Automatic 100, escalating',
        })

    return {
        'status': 'ok',
        'task': f'Manage company {company_number}',
        'capability_level': 5,
        'workflow_steps': [
            {'step': 1, 'task': 'File Confirmation Statement annually', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/file-confirmation-statement', 'deadline': 'Every year, within 14 days of anniversary'},
            {'step': 2, 'task': 'File Annual Accounts', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/file-company-accounts', 'deadline': '9 months after accounting period end'},
            {'step': 3, 'task': 'File Corporation Tax Return', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/file-company-tax-return', 'deadline': '12 months after accounting period end'},
            {'step': 4, 'task': 'Pay Corporation Tax', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/pay-corporation-tax', 'deadline': '9 months and 1 day after accounting period end'},
            {'step': 5, 'task': 'VAT returns (if registered)', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vat-returns', 'deadline': 'Quarterly'},
            {'step': 6, 'task': 'Update Companies House records', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/update-company-information'},
            {'step': 7, 'task': 'Maintain PSC register', 'action_class': 'USER_HANDOFF'},
        ],
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
        'official_urls': [
            'https://www.gov.uk/file-confirmation-statement',
            'https://www.gov.uk/file-company-accounts',
            'https://www.gov.uk/file-company-tax-return',
            'https://www.gov.uk/pay-corporation-tax',
            'https://www.gov.uk/update-company-information',
        ],
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
    }


def change_details_everywhere(detail_type, old_value, new_value):
    if detail_type.lower() not in ('name', 'address'):
        return {'status': 'error', 'message': 'detail_type must be "name" or "address"'}

    orgs = []
    if detail_type.lower() == 'name':
        orgs = [
            {'org': 'DVLA - Driving Licence', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/change-driving-licence/details', 'fee': 'Free'},
            {'org': 'HMRC - Tax records', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/update-hmrc-your-personal-details', 'fee': 'Free'},
            {'org': 'HM Passport Office', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/renew-adult-passport', 'fee': '82.50', 'note': 'Name change requires passport renewal'},
            {'org': 'Banks and building societies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Electoral roll', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/register-to-vote', 'fee': 'Free'},
            {'org': 'NHS - GP registration', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'DVLA - Vehicle tax', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vehicle-tax', 'fee': 'Free'},
            {'org': 'Employer / payroll', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Pension providers', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Insurance policies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'HM Land Registry (if property owner)', 'action_class': 'USER_HANDOFF', 'fee': 'Varies'},
        ]
    else:
        orgs = [
            {'org': 'DVLA - Driving Licence', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/change-address-driving-licence', 'fee': 'Free'},
            {'org': 'DVLA - Vehicle tax', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vehicle-tax', 'fee': 'Free'},
            {'org': 'HMRC - Tax records', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/update-hmrc-your-personal-details', 'fee': 'Free'},
            {'org': 'Electoral roll', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/register-to-vote', 'fee': 'Free'},
            {'org': 'Council tax', 'action_class': 'USER_HANDOFF', 'url': 'https://www.gov.uk/find-local-council', 'fee': 'Free'},
            {'org': 'Banks and building societies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'NHS - GP registration', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Insurance policies', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'Employer / payroll', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
            {'org': 'HMRC - National Insurance record', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/personal-tax-account', 'fee': 'Free'},
            {'org': 'HM Land Registry (if property owner)', 'action_class': 'USER_HANDOFF', 'fee': 'Varies'},
            {'org': 'Student loan company', 'action_class': 'USER_HANDOFF', 'fee': 'Free'},
        ]

    agent_items = [o for o in orgs if o['action_class'] in ('AUTO', 'APPROVAL_REQUIRED')]
    user_items = [o for o in orgs if o['action_class'] == 'USER_HANDOFF']

    return {
        'status': 'ok',
        'task': f'Change {detail_type} everywhere',
        'capability_level': 5,
        'workflow_steps': [{'step': i + 1, **org} for i, org in enumerate(orgs)],
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
        'official_urls': [o['url'] for o in orgs if o.get('url')],
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
    }


def renew_passport():
    workflow_steps = [
        {
            'step': 1, 'task': 'Check passport eligibility for online renewal',
            'what': 'Passport must be undamaged, issued within last 15 years, issued when 16+',
            'action_class': 'AUTO',
            'url': 'https://www.gov.uk/renew-adult-passport',
        },
        {
            'step': 2, 'task': 'Get a digital photo',
            'what': 'White background, taken within last month, specific size',
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/passport-photo-guidelines',
        },
        {
            'step': 3, 'task': 'Complete online application',
            'what': 'Fill in the GOV.UK form',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/renew-adult-passport',
        },
        {
            'step': 4, 'task': 'Pay for renewal',
            'what': 'Online: 82.50. Post Office Check & Send: 92.50',
            'action_class': 'APPROVAL_REQUIRED',
            'fee': '82.50 online / 92.50 with Check & Send',
        },
        {
            'step': 5, 'task': 'Post old passport',
            'what': 'Send old passport to HM Passport Office',
            'action_class': 'USER_HANDOFF',
        },
        {
            'step': 6, 'task': 'Wait for new passport',
            'what': 'Processing takes up to 10 weeks',
            'action_class': 'USER_HANDOFF',
            'takes': 'Up to 10 weeks',
        },
        {
            'step': 7, 'task': 'Sign new passport immediately',
            'what': 'An unsigned passport is not valid',
            'action_class': 'USER_HANDOFF',
        },
    ]

    return {
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
        'official_urls': [
            'https://www.gov.uk/renew-adult-passport',
            'https://www.gov.uk/passport-photo-guidelines',
            'https://www.gov.uk/apply-renew-passport',
        ],
        'failure_modes': [
            'Photo does not meet requirements (application delayed)',
            'Not signing new passport (invalid document)',
            'Underestimating processing time (missed travel)',
        ],
        'follow_up_dates': [
            'Set reminder: check passport 6 months before international travel',
            'Set reminder: renew 10 weeks before expiry',
        ],
    }


def start_driving():
    workflow_steps = [
        {
            'step': 1, 'task': 'Apply for provisional driving licence',
            'what': 'Must be 15 years and 9 months old to apply',
            'action_class': 'APPROVAL_REQUIRED',
            'url': 'https://www.gov.uk/apply-first-provisional-driving-licence',
            'fee': '34 online / 43 by post',
            'takes': 'Up to 3 weeks',
        },
        {
            'step': 2, 'task': 'Book and take theory test',
            'what': 'Multiple choice and hazard perception',
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/book-driving-test',
            'fee': '23',
            'prereq': 'Provisional licence in hand',
        },
        {
            'step': 3, 'task': 'Book and take practical driving test',
            'what': 'Driving test with examiner',
            'action_class': 'USER_HANDOFF',
            'url': 'https://www.gov.uk/book-driving-test',
            'fee': '62 weekday / 75 weekend',
            'prereq': 'Passed theory test',
        },
        {
            'step': 4, 'task': 'Receive full driving licence',
            'what': 'DVLA sends your full licence',
            'action_class': 'USER_HANDOFF',
            'takes': 'About 3 weeks after passing',
        },
    ]

    return {
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
        'official_urls': [
            'https://www.gov.uk/apply-first-provisional-driving-licence',
            'https://www.gov.uk/practical-driving-test',
            'https://www.gov.uk/theory-test',
            'https://www.gov.uk/book-driving-test',
        ],
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
    }


def start_regulated_business(business_type):
    business_lower = business_type.lower().strip()

    workflows = {
        'food': {
            'name': 'Food Business Registration',
            'authority': 'Local Council Environmental Health',
            'url': 'https://www.gov.uk/starting-food-business',
            'fee': 'Free',
            'deadline': 'At least 28 days before opening',
            'steps': [
                {'step': 1, 'task': 'Register food business with local council', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/starting-food-business', 'fee': 'Free'},
                {'step': 2, 'task': 'Create a Food Safety Management System', 'action_class': 'USER_HANDOFF', 'url': 'https://www.food.gov.uk/business-guidance/starting-up'},
                {'step': 3, 'task': 'Get food hygiene rating assessment', 'action_class': 'USER_HANDOFF'},
                {'step': 4, 'task': 'Ensure premises meet regulations', 'action_class': 'USER_HANDOFF'},
                {'step': 5, 'task': 'Staff food hygiene training', 'action_class': 'USER_HANDOFF'},
                {'step': 6, 'task': 'Allergen information compliance', 'action_class': 'USER_HANDOFF', 'url': 'https://www.food.gov.uk/allergens'},
            ],
        },
        'premises': {
            'name': 'Licensed Premises (Alcohol/Selling Late)',
            'authority': 'Local Council Licensing',
            'url': 'https://www.gov.uk/find-licences/premises-licence',
            'fee': '100-635 (based on rateable value)',
            'deadline': 'Apply before opening',
            'steps': [
                {'step': 1, 'task': 'Apply for premises licence', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/find-licences/premises-licence', 'fee': '100-635'},
                {'step': 2, 'task': 'Designate a Designated Premises Supervisor (DPS)', 'action_class': 'USER_HANDOFF'},
                {'step': 3, 'task': 'Apply for personal licence (DPS)', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/find-licences/personal-licence', 'fee': '37'},
                {'step': 4, 'task': 'Complete licensing objectives training', 'action_class': 'USER_HANDOFF'},
                {'step': 5, 'task': 'Display licence and notices', 'action_class': 'USER_HANDOFF'},
                {'step': 6, 'task': 'Notify responsible authorities', 'action_class': 'AUTO'},
            ],
        },
        'taxi': {
            'name': 'Private Hire / Taxi Driver Licence',
            'authority': 'Local Council',
            'url': 'https://www.gov.uk/private-hire-vehicle-licence',
            'fee': 'Varies by council',
            'deadline': 'Before driving',
            'steps': [
                {'step': 1, 'task': 'Apply for private hire driver licence', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/private-hire-vehicle-licence', 'fee': 'Varies'},
                {'step': 2, 'task': 'DBS check', 'action_class': 'USER_HANDOFF'},
                {'step': 3, 'task': 'Medical examination', 'action_class': 'USER_HANDOFF'},
                {'step': 4, 'task': 'Topographical test', 'action_class': 'USER_HANDOFF'},
                {'step': 5, 'task': 'Driving test (if required)', 'action_class': 'USER_HANDOFF'},
                {'step': 6, 'task': 'Apply for vehicle licence', 'action_class': 'APPROVAL_REQUIRED', 'fee': 'Varies'},
            ],
        },
        'construction': {
            'name': 'Construction Business',
            'authority': 'HSE / Local Council',
            'url': 'https://www.hse.gov.uk/construction/',
            'fee': 'Free registration',
            'deadline': 'Before starting work',
            'steps': [
                {'step': 1, 'task': 'Register as a construction business', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.hse.gov.uk/construction/', 'fee': 'Free'},
                {'step': 2, 'task': 'Health and safety policy', 'action_class': 'USER_HANDOFF'},
                {'step': 3, 'task': 'Public liability insurance', 'action_class': 'USER_HANDOFF'},
                {'step': 4, 'task': 'CSCS cards for workers', 'action_class': 'USER_HANDOFF', 'url': 'https://www.cscs.co.uk/'},
                {'step': 5, 'task': 'Waste carrier licence', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/guidance/register-as-a-waste-carrier', 'fee': '154 for 3 years'},
            ],
        },
    }

    workflow = workflows.get(business_lower)
    if not workflow:
        return {'status': 'error', 'message': f'Unknown business type: {business_type}', 'available_types': list(workflows.keys())}

    agent_items = [s for s in workflow['steps'] if s['action_class'] in ('AUTO', 'APPROVAL_REQUIRED')]
    user_items = [s for s in workflow['steps'] if s['action_class'] == 'USER_HANDOFF']

    return {
        'status': 'ok',
        'task': f'Start regulated business: {workflow["name"]}',
        'capability_level': 3,
        'workflow_steps': workflow['steps'],
        'agent_actions': [s['task'] for s in agent_items],
        'user_actions': [s['task'] for s in user_items],
        'required_documents': ['Business plan', 'Premises details', 'Insurance documents', 'Staff training records'],
        'deadlines': [f'{workflow["name"]}: {workflow["deadline"]}'],
        'fees': [f'{workflow["name"]}: {workflow["fee"]}'],
        'official_urls': [s['url'] for s in workflow['steps'] if s.get('url')],
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
    }


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
                {'step': 1, 'task': 'Identify amount and deadline', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Check if amount is correct', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-income-tax-returns'},
                {'step': 3, 'task': 'Set up payment plan if needed', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/pay-self-assessment-tax-bill'},
                {'step': 4, 'task': 'Dispute if incorrect', 'action_class': 'USER_HANDOFF', 'url': 'https://www.gov.uk/claim-tax-refund'},
            ],
            'agent_actions': ['Identify deadline and amount', 'Check tax account', 'Set up payment plan'],
            'user_actions': ['Approve payment', 'Provide bank details', 'Dispute if needed'],
        },
        'mot_expiry': {
            'task': 'Renew MOT',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Check current MOT status', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-mot-history'},
                {'step': 2, 'task': 'Book MOT test', 'action_class': 'USER_HANDOFF', 'url': 'https://www.gov.uk/get-mot'},
                {'step': 3, 'task': 'Take vehicle to test', 'action_class': 'USER_HANDOFF'},
            ],
            'agent_actions': ['Check MOT status', 'Find local garages'],
            'user_actions': ['Book test', 'Take vehicle', 'Pay garage'],
        },
        'tax_expiry': {
            'task': 'Renew vehicle tax',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Check vehicle tax status', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/check-vehicle-tax'},
                {'step': 2, 'task': 'Ensure valid MOT', 'action_class': 'AUTO'},
                {'step': 3, 'task': 'Tax vehicle online', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vehicle-tax'},
            ],
            'agent_actions': ['Check tax status', 'Verify MOT validity'],
            'user_actions': ['Pay for tax renewal'],
        },
        'passport_expiry': {
            'task': 'Renew passport',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Check eligibility for online renewal', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Get digital photo', 'action_class': 'USER_HANDOFF'},
                {'step': 3, 'task': 'Apply online', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/renew-adult-passport'},
                {'step': 4, 'task': 'Post old passport', 'action_class': 'USER_HANDOFF'},
            ],
            'agent_actions': ['Check eligibility', 'Guide application'],
            'user_actions': ['Get photo', 'Pay', 'Post documents'],
        },
        'council_tax': {
            'task': 'Handle council tax matter',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify council and issue', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Contact council', 'action_class': 'USER_HANDOFF', 'url': 'https://www.gov.uk/find-local-council'},
                {'step': 3, 'task': 'Check for discounts or exemptions', 'action_class': 'APPROVAL_REQUIRED'},
            ],
            'agent_actions': ['Find council contact', 'Check for discounts'],
            'user_actions': ['Contact council', 'Provide evidence'],
        },
        'driving_licence': {
            'task': 'Handle driving licence matter',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify specific issue', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Follow DVLA guidance', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/browse/driving'},
                {'step': 3, 'task': 'Submit required forms', 'action_class': 'APPROVAL_REQUIRED'},
            ],
            'agent_actions': ['Identify issue', 'Guide process'],
            'user_actions': ['Submit forms', 'Provide documents'],
        },
        'company_filing': {
            'task': 'Handle company filing matter',
            'capability_level': 4,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify filing requirement', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Prepare documents', 'action_class': 'APPROVAL_REQUIRED'},
                {'step': 3, 'task': 'File with Companies House', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/file-confirmation-statement'},
            ],
            'agent_actions': ['Identify requirement', 'Prepare templates'],
            'user_actions': ['Approve accounts', 'Authorise filing'],
        },
        'benefits': {
            'task': 'Handle benefits matter',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify benefit and action required', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Check eligibility', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/benefits-calculators'},
                {'step': 3, 'task': 'Contact DWP or apply', 'action_class': 'USER_HANDOFF'},
            ],
            'agent_actions': ['Identify benefit', 'Check calculator'],
            'user_actions': ['Contact DWP', 'Provide information'],
        },
        'insurance': {
            'task': 'Handle insurance matter',
            'capability_level': 2,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify type of insurance', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Check renewal date', 'action_class': 'AUTO'},
                {'step': 3, 'task': 'Compare or renew', 'action_class': 'USER_HANDOFF'},
            ],
            'agent_actions': ['Identify renewal date', 'Compare options'],
            'user_actions': ['Make final decision', 'Pay'],
        },
        'court_fine': {
            'task': 'Handle court fine or penalty',
            'capability_level': 2,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify fine amount and deadline', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Check if you can appeal', 'action_class': 'APPROVAL_REQUIRED'},
                {'step': 3, 'task': 'Pay or set up payment plan', 'action_class': 'APPROVAL_REQUIRED'},
            ],
            'agent_actions': ['Identify details', 'Check appeal options'],
            'user_actions': ['Decide to pay or appeal', 'Pay'],
        },
        'v5c': {
            'task': 'Handle V5C matter',
            'capability_level': 3,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify V5C issue', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Contact DVLA', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vehicle-registration'},
                {'step': 3, 'task': 'Order replacement if needed', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/vehicle-registration', 'fee': 'Free'},
            ],
            'agent_actions': ['Identify issue', 'Guide DVLA process'],
            'user_actions': ['Contact DVLA', 'Provide details'],
        },
        'electoral': {
            'task': 'Handle electoral matter',
            'capability_level': 2,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify issue', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Register or update', 'action_class': 'APPROVAL_REQUIRED', 'url': 'https://www.gov.uk/register-to-vote'},
            ],
            'agent_actions': ['Identify issue', 'Guide registration'],
            'user_actions': ['Provide NI number', 'Confirm address'],
        },
        'medical': {
            'task': 'Handle NHS/medical matter',
            'capability_level': 1,
            'workflow_steps': [
                {'step': 1, 'task': 'Identify issue', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Direct to appropriate NHS service', 'action_class': 'AUTO', 'url': 'https://www.nhs.uk'},
            ],
            'agent_actions': ['Identify service', 'Provide NHS links'],
            'user_actions': ['Contact service directly'],
        },
        'unknown': {
            'task': 'Unclear government letter',
            'capability_level': 1,
            'workflow_steps': [
                {'step': 1, 'task': 'Scan letter for sender name and logo', 'action_class': 'AUTO'},
                {'step': 2, 'task': 'Check for reference numbers', 'action_class': 'AUTO'},
                {'step': 3, 'task': 'Contact sender to clarify', 'action_class': 'USER_HANDOFF'},
            ],
            'agent_actions': ['Help identify sender'],
            'user_actions': ['Contact sender', 'Provide letter details'],
        },
    }

    primary = matched[0]
    workflow = workflows.get(primary, workflows['unknown'])

    return {
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
        'official_urls': [s['url'] for s in workflow['workflow_steps'] if s.get('url')],
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
    }


def admin_audit(current_state):
    checks = []
    now = datetime.now()

    if isinstance(current_state, str):
        try:
            current_state = json.loads(current_state)
        except (json.JSONDecodeError, TypeError):
            current_state = {}

    if not current_state:
        return {
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
        for deadline in comp.get('deadlines', []):
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

    return {
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
                        'url': 'https://www.gov.uk/get-mot',
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
                        'url': 'https://www.gov.uk/vehicle-tax',
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
                            'url': 'https://www.gov.uk/file-confirmation-statement',
                        })
                except (ValueError, TypeError):
                    pass

    expiring.sort(key=lambda x: x.get('days_remaining', 9999))

    return {
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
                    "serverInfo": {"name": "uk_admin", "version": "2.0.0",
                                   "description": "UK Admin - Get boring British things done. 12 Boring UK workflow capabilities with action classification, capability levels, and full lifecycle management."},
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
        print(json.dumps({"name": "uk_admin", "version": "2.0.0", "tools": [t["name"] for t in TOOLS]}, indent=2))
