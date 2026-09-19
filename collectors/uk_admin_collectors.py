#!/usr/bin/env python3
"""
UK Admin — Collectors

Seeds the UK Admin garden with official government task data.

Sources:
1. GOV.UK API - All government services, guidance, and transactions
2. GOV.UK One Login - Authentication status tracking
3. Companies House API - Company setup/management
4. DVLA/DVSA - Vehicle and driving services
5. HMRC - Tax obligations
6. Council data - Local authority services

Usage:
    python -m collectors.uk_admin_collectors --seed-govuk
    python -m collectors.uk_admin_collectors --seed-all
"""

import json
import os
import sys
import hashlib
import argparse
from datetime import datetime, date
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'uk_admin' / 'data'
sys.path.insert(0, str(ROOT))

GOVUK_API = 'https://www.gov.uk/api'
COMPANIES_HOUSE_API = 'https://api.company-information.service.gov.uk'

TODAY = date.today().isoformat()


# ============================================================
# Raw Collectors — pull from GOV.UK APIs
# ============================================================

def collect_govuk_services() -> dict:
    """Collect all GOV.UK services from the API.
    GET https://www.gov.uk/api/services
    Returns: list of all government services with their URLs, requirements, costs."""
    try:
        resp = requests.get(f'{GOVUK_API}/services', timeout=30)
        if resp.status_code == 200:
            services = resp.json()
            return {
                'status': 'ok',
                'source': 'govuk_api',
                'count': len(services),
                'services': services,
                'collected_at': datetime.now().isoformat(),
            }
        return {
            'status': 'error',
            'source': 'govuk_api',
            'http_status': resp.status_code,
            'message': resp.text[:500],
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'source': 'govuk_api',
            'message': str(e),
        }


def collect_govuk_transactions() -> dict:
    """Collect all GOV.UK transactions (online services).
    GET https://www.gov.uk/api/transactions
    Returns: list of all transactions with in-progress/done URLs."""
    try:
        resp = requests.get(f'{GOVUK_API}/transactions', timeout=30)
        if resp.status_code == 200:
            transactions = resp.json()
            return {
                'status': 'ok',
                'source': 'govuk_api',
                'count': len(transactions),
                'transactions': transactions,
                'collected_at': datetime.now().isoformat(),
            }
        return {
            'status': 'error',
            'source': 'govuk_api',
            'http_status': resp.status_code,
            'message': resp.text[:500],
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'source': 'govuk_api',
            'message': str(e),
        }


def collect_govuk_organisations() -> dict:
    """Collect all GOV.UK organisations.
    GET https://www.gov.uk/api/organisations"""
    try:
        resp = requests.get(f'{GOVUK_API}/organisations', timeout=30)
        if resp.status_code == 200:
            orgs = resp.json()
            return {
                'status': 'ok',
                'source': 'govuk_api',
                'count': len(orgs),
                'organisations': orgs,
                'collected_at': datetime.now().isoformat(),
            }
        return {
            'status': 'error',
            'source': 'govuk_api',
            'http_status': resp.status_code,
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'source': 'govuk_api',
            'message': str(e),
        }


def collect_govuk_content(service_slug: str) -> dict:
    """Collect detailed content for a specific service.
    GET https://www.gov.uk/api/content/{service_slug}"""
    try:
        resp = requests.get(f'{GOVUK_API}/content/{service_slug}', timeout=15)
        if resp.status_code == 200:
            return {
                'status': 'ok',
                'source': 'govuk_api',
                'slug': service_slug,
                'data': resp.json(),
                'collected_at': datetime.now().isoformat(),
            }
        return {
            'status': 'error',
            'source': 'govuk_api',
            'slug': service_slug,
            'http_status': resp.status_code,
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'source': 'govuk_api',
            'slug': service_slug,
            'message': str(e),
        }


# ============================================================
# Normalizers — map GOV.UK data to canonical UK Admin form
# ============================================================

def normalize_service(raw: dict) -> dict:
    """Normalize a GOV.UK service into canonical form."""
    slug = raw.get('slug', raw.get('id', ''))
    org = raw.get('organisation', {})
    org_title = org.get('title', '') if isinstance(org, dict) else str(org)

    return {
        'service_id': slug,
        'service_name': raw.get('title', raw.get('name', '')),
        'organisation': org_title,
        'url': f'https://www.gov.uk/{slug}',
        'transaction_url': raw.get('transaction_url', ''),
        'done_url': raw.get('done_url', ''),
        'cost_gbp': 0.0,
        'auth_required': False,
        'one_login': False,
        'agent_accessible': False,
        'source': 'govuk',
        'observed_at': datetime.now().isoformat(),
    }


def normalize_transaction(raw: dict) -> dict:
    """Normalize a GOV.UK transaction into canonical form."""
    slug = raw.get('slug', raw.get('id', ''))
    org = raw.get('organisation', {})
    org_title = org.get('title', '') if isinstance(org, dict) else str(org)

    return {
        'service_id': slug,
        'service_name': raw.get('title', raw.get('name', '')),
        'organisation': org_title,
        'url': f'https://www.gov.uk/{slug}',
        'transaction_url': raw.get('in_progress_url', ''),
        'done_url': raw.get('done_url', ''),
        'cost_gbp': 0.0,
        'auth_required': False,
        'one_login': False,
        'agent_accessible': False,
        'source': 'govuk',
        'observed_at': datetime.now().isoformat(),
    }


def normalize_task(task_name: str, task_data: dict) -> dict:
    """Normalize an admin task into canonical form.
    Merges curated task definitions with API data where available."""
    now = datetime.now().isoformat()

    return {
        'task_id': task_data.get('task_id', _slugify(task_name)),
        'task_name': task_data.get('task_name', task_name),
        'category': task_data.get('category', 'general'),
        'subcategory': task_data.get('subcategory', ''),
        'authority': task_data.get('authority', 'GOV.UK'),
        'jurisdiction': task_data.get('jurisdiction', 'GB'),
        'url': task_data.get('url', ''),
        'cost_gbp': task_data.get('cost_gbp', 0.0),
        'takes_time': task_data.get('takes_time', ''),
        'requires': task_data.get('requires', []),
        'agent_permissions': task_data.get('agent_permissions', {
            'explain': True,
            'gather_requirements': True,
            'prefill': False,
            'submit': False,
            'payment': 'not_possible',
            'retain_credentials': False,
        }),
        'failure_modes': task_data.get('failure_modes', []),
        'official_source': task_data.get('official_source', task_data.get('url', '')),
        'last_verified': task_data.get('last_verified', TODAY),
        'is_recurring': task_data.get('is_recurring', False),
        'recurrence': task_data.get('recurrence', ''),
        'related_tasks': task_data.get('related_tasks', []),
        'commercial_needs': task_data.get('commercial_needs', []),
        'source': task_data.get('source', 'curated'),
        'observed_at': task_data.get('observed_at', now),
    }


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = text.strip('_')
    return text


# ============================================================
# Curated UK Admin Tasks — the core knowledge base
# ============================================================

CURATED_TASKS = {
    # --- DRIVING ---
    'renew_driving_licence': {
        'task_name': 'Renew your driving licence',
        'category': 'driving',
        'subcategory': 'licence',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/renew-driving-licence',
        'cost_gbp': 14.00,
        'takes_time': '3 weeks',
        'requires': ['identity', 'licence_details', 'address', 'photo'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['identity_mismatch', 'address_mismatch', 'expired_documents'],
        'official_source': 'https://www.gov.uk/renew-driving-licence',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'every 10 years',
        'related_tasks': ['update_address', 'replace_lost_licence'],
        'commercial_needs': ['insurance', 'breakdown_cover'],
    },
    'replace_lost_licence': {
        'task_name': 'Replace a lost or stolen driving licence',
        'category': 'driving',
        'subcategory': 'licence',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/replace-driving-licence',
        'cost_gbp': 20.00,
        'takes_time': '3 weeks',
        'requires': ['identity', 'address', 'photo', 'lost_or_stolen_declaration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['identity_mismatch', 'address_mismatch', 'previous_licence_disqualified'],
        'official_source': 'https://www.gov.uk/replace-driving-licence',
        'last_verified': '2026-09-19',
        'related_tasks': ['renew_driving_licence', 'update_address'],
        'commercial_needs': ['insurance', 'breakdown_cover'],
    },
    'update_address': {
        'task_name': 'Change the address on your driving licence',
        'category': 'driving',
        'subcategory': 'licence',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/change-address-driving-licence',
        'cost_gbp': 0.00,
        'takes_time': '3 weeks',
        'requires': ['identity', 'new_address', 'old_address'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['address_mismatch', 'name_mismatch'],
        'official_source': 'https://www.gov.uk/change-address-driving-licence',
        'last_verified': '2026-09-19',
        'related_tasks': ['renew_driving_licence', 'update_vehicle_tax'],
        'commercial_needs': ['insurance', 'vehicle_tax'],
    },
    'view_licence_points': {
        'task_name': 'Check your driving licence information',
        'category': 'driving',
        'subcategory': 'licence',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/view-driving-licence',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['driving_licence_number', 'national_insurance_number'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/view-driving-licence',
        'last_verified': '2026-09-19',
        'related_tasks': ['renew_driving_licence'],
    },

    # --- VEHICLE ---
    'check_mot': {
        'task_name': 'Check MOT history of a vehicle',
        'category': 'vehicle',
        'subcategory': 'mot',
        'authority': 'DVSA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/check-mot-history',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/check-mot-history',
        'last_verified': '2026-09-19',
        'related_tasks': ['book_mot', 'check_vehicle_tax'],
        'commercial_needs': ['breakdown_cover', 'car_insurance'],
    },
    'book_mot': {
        'task_name': 'Book an MOT',
        'category': 'vehicle',
        'subcategory': 'mot',
        'authority': 'DVSA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/get-mot',
        'cost_gbp': 54.85,
        'takes_time': '1 hour',
        'requires': ['vehicle_registration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['vehicle_not_roadworthy'],
        'official_source': 'https://www.gov.uk/get-mot',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'every 12 months',
        'related_tasks': ['check_mot', 'check_vehicle_tax'],
        'commercial_needs': ['breakdown_cover', 'car_insurance'],
    },
    'check_vehicle_tax': {
        'task_name': 'Check vehicle tax',
        'category': 'vehicle',
        'subcategory': 'tax',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/check-vehicle-tax',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/check-vehicle-tax',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_vehicle_tax', 'check_mot'],
    },
    'update_vehicle_tax': {
        'task_name': 'Tax your vehicle',
        'category': 'vehicle',
        'subcategory': 'tax',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/vehicle-tax',
        'cost_gbp': 0.00,  # varies by vehicle
        'takes_time': 'instant',
        'requires': ['vehicle_registration', 'insurance', 'mot_certificate'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['no_insurance', 'no_mot'],
        'official_source': 'https://www.gov.uk/vehicle-tax',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'every 6 or 12 months',
        'related_tasks': ['check_vehicle_tax', 'book_mot'],
        'commercial_needs': ['car_insurance'],
    },
    'sorn_vehicle': {
        'task_name': 'Declare a vehicle off the road (SORN)',
        'category': 'vehicle',
        'subcategory': 'tax',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/sorn-statutory-off-road-notification',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['vehicle_registration', 'insurance_or_sorn_declaration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/sorn-statutory-off-road-notification',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_vehicle_tax'],
    },
    'transfer_vehicle': {
        'task_name': 'Sell or transfer a vehicle',
        'category': 'vehicle',
        'subcategory': 'ownership',
        'authority': 'DVLA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/sold-bought-vehicle',
        'cost_gbp': 0.00,
        'takes_time': '1-5 days',
        'requires': ['vehicle_registration', 'new_keeper_details', 'v5c'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['incomplete_v5c', 'new_keeper_details_wrong'],
        'official_source': 'https://www.gov.uk/sold-bought-vehicle',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_vehicle_tax', 'sorn_vehicle'],
    },
    'check_mot_failures': {
        'task_name': 'Check common MOT failures',
        'category': 'vehicle',
        'subcategory': 'mot',
        'authority': 'DVSA',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/check-mot-history',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/check-mot-history',
        'last_verified': '2026-09-19',
        'related_tasks': ['book_mot', 'check_mot'],
    },

    # --- PASSPORT ---
    'apply_passport': {
        'task_name': 'Apply for a UK passport',
        'category': 'passport',
        'subcategory': 'application',
        'authority': 'HM Passport Office',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/apply-renew-passport',
        'cost_gbp': 82.50,
        'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'birth_certificate', 'countersignatory'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['photo_rejected', 'insufficient_documents', 'countersignatory_issue'],
        'official_source': 'https://www.gov.uk/apply-renew-passport',
        'last_verified': '2026-09-19',
        'related_tasks': ['renew_passport', 'replace_lost_passport'],
        'commercial_needs': ['travel_insurance'],
    },
    'renew_passport': {
        'task_name': 'Renew your passport',
        'category': 'passport',
        'subcategory': 'renewal',
        'authority': 'HM Passport Office',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/renew-adult-passport',
        'cost_gbp': 82.50,
        'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'existing_passport'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['photo_rejected', 'name_change_not_documented'],
        'official_source': 'https://www.gov.uk/renew-adult-passport',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'every 10 years',
        'related_tasks': ['apply_passport', 'replace_lost_passport'],
        'commercial_needs': ['travel_insurance'],
    },
    'replace_lost_passport': {
        'task_name': 'Replace a lost or stolen passport',
        'category': 'passport',
        'subcategory': 'replacement',
        'authority': 'HM Passport Office',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/replace-lost-stolen-passport',
        'cost_gbp': 82.50,
        'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'lost_or_stolen_declaration', 'birth_certificate'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['photo_rejected', 'previous_passport_fraud_flag'],
        'official_source': 'https://www.gov.uk/replace-lost-stolen-passport',
        'last_verified': '2026-09-19',
        'related_tasks': ['renew_passport', 'apply_passport'],
    },
    'report_passport_lost': {
        'task_name': 'Report a lost or stolen passport',
        'category': 'passport',
        'subcategory': 'security',
        'authority': 'HM Passport Office',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/report-a-lost-or-stolen-passport',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['passport_number', 'personal_details'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/report-a-lost-or-stolen-passport',
        'last_verified': '2026-09-19',
        'related_tasks': ['replace_lost_passport'],
    },

    # --- TAX ---
    'self_assessment_register': {
        'task_name': 'Register for Self Assessment',
        'category': 'tax',
        'subcategory': 'self_assessment',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/register-for-self-assessment',
        'cost_gbp': 0.00,
        'takes_time': '10 working days',
        'requires': ['identity', 'national_insurance_number', 'employment_history'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['already_registered', 'insufficient_income'],
        'official_source': 'https://www.gov.uk/register-for-self-assessment',
        'last_verified': '2026-09-19',
        'related_tasks': ['self_assessment_submit', 'tax_return'],
    },
    'self_assessment_submit': {
        'task_name': 'Complete your Self Assessment tax return',
        'category': 'tax',
        'subcategory': 'self_assessment',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/self-assessment-tax-returns',
        'cost_gbp': 0.00,
        'takes_time': '1-3 hours',
        'requires': ['identity', 'national_insurance_number', 'income_details', 'expenses', 'p60'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['incomplete_return', 'late_filing_penalty', 'incorrect_tax_calculation'],
        'official_source': 'https://www.gov.uk/self-assessment-tax-returns',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'annually by 31 January',
        'related_tasks': ['self_assessment_register', 'pay_tax_bill'],
        'commercial_needs': ['accountant', 'tax_software'],
    },
    'pay_tax_bill': {
        'task_name': 'Pay your Self Assessment tax bill',
        'category': 'tax',
        'subcategory': 'payment',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/pay-self-assessment-tax-bill',
        'cost_gbp': 0.00,
        'takes_time': 'instant to 5 working days',
        'requires': ['identity', 'tax_reference', 'payment_method'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['insufficient_funds', 'incorrect_amount', 'late_payment_interest'],
        'official_source': 'https://www.gov.uk/pay-self-assessment-tax-bill',
        'last_verified': '2026-09-19',
        'related_tasks': ['self_assessment_submit'],
        'commercial_needs': ['accountant'],
    },
    'check_tax_code': {
        'task_name': 'Check your tax code',
        'category': 'tax',
        'subcategory': 'employment',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/check-income-tax-returns',
        'cost_gbp': 0.00,
        'takes_time': 'instant',
        'requires': ['identity', 'national_insurance_number'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/check-income-tax-returns',
        'last_verified': '2026-09-19',
        'related_tasks': ['self_assessment_register'],
    },
    'claim_tax_refund': {
        'task_name': 'Claim a tax refund',
        'category': 'tax',
        'subcategory': 'refund',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/claim-tax-refund',
        'cost_gbp': 0.00,
        'takes_time': '6 weeks',
        'requires': ['identity', 'p60', 'p45', 'bank_details'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['insufficient_evidence', 'already_refunded'],
        'official_source': 'https://www.gov.uk/claim-tax-refund',
        'last_verified': '2026-09-19',
        'related_tasks': ['self_assessment_submit', 'check_tax_code'],
    },

    # --- BUSINESS ---
    'setup_sole_trader': {
        'task_name': 'Set up as a sole trader',
        'category': 'business',
        'subcategory': 'self_employment',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/working-for-yourself',
        'cost_gbp': 0.00,
        'takes_time': '10 working days for UTR',
        'requires': ['identity', 'national_insurance_number', 'business_details'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['already_registered', 'insufficient_business_details'],
        'official_source': 'https://www.gov.uk/working-for-yourself',
        'last_verified': '2026-09-19',
        'related_tasks': ['self_assessment_register', 'register_for_vat'],
        'commercial_needs': ['accountant', 'business_insurance', 'business_bank_account'],
    },
    'register_limited_company': {
        'task_name': 'Register a limited company',
        'category': 'business',
        'subcategory': 'company_formation',
        'authority': 'Companies House',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/limited-company-formation',
        'cost_gbp': 12.00,
        'takes_time': '24 hours',
        'requires': ['identity', 'registered_address', 'directors', 'shareholders', 'articles_of_association'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['name_taken', 'incorrect_articles', 'director_disqualified'],
        'official_source': 'https://www.gov.uk/limited-company-formation',
        'last_verified': '2026-09-19',
        'related_tasks': ['register_corporation_tax', 'register_for_vat', 'pay_corporation_tax'],
        'commercial_needs': ['accountant', 'business_bank_account', 'business_insurance'],
    },
    'register_for_vat': {
        'task_name': 'Register for VAT',
        'category': 'business',
        'subcategory': 'vat',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/register-for-vat',
        'cost_gbp': 0.00,
        'takes_time': '14 working days',
        'requires': ['identity', 'business_details', 'turnover_above_threshold'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['below_threshold', 'already_registered'],
        'official_source': 'https://www.gov.uk/register-for-vat',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'quarterly returns',
        'related_tasks': ['submit_vat_return'],
        'commercial_needs': ['accountant', 'accounting_software'],
    },
    'submit_vat_return': {
        'task_name': 'Submit a VAT return',
        'category': 'business',
        'subcategory': 'vat',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/vat-returns',
        'cost_gbp': 0.00,
        'takes_time': '30 minutes',
        'requires': ['identity', 'vat_number', 'turnover_data'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['incorrect_figures', 'late_filing_penalty'],
        'official_source': 'https://www.gov.uk/vat-returns',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'quarterly',
        'related_tasks': ['register_for_vat'],
        'commercial_needs': ['accountant', 'accounting_software'],
    },
    'register_corporation_tax': {
        'task_name': 'Register for Corporation Tax',
        'category': 'business',
        'subcategory': 'corporation_tax',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/register-for-corporation-tax',
        'cost_gbp': 0.00,
        'takes_time': '15 working days',
        'requires': ['company_number', 'company_name', 'date_of_comencement'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['already_registered', 'company_not_found'],
        'official_source': 'https://www.gov.uk/register-for-corporation-tax',
        'last_verified': '2026-09-19',
        'related_tasks': ['pay_corporation_tax', 'register_limited_company'],
    },
    'pay_corporation_tax': {
        'task_name': 'Pay Corporation Tax',
        'category': 'business',
        'subcategory': 'corporation_tax',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/pay-corporation-tax',
        'cost_gbp': 0.00,
        'takes_time': 'instant to 5 working days',
        'requires': ['company_number', 'payment_method', 'amount_due'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['insufficient_funds', 'incorrect_amount'],
        'official_source': 'https://www.gov.uk/pay-corporation-tax',
        'last_verified': '2026-09-19',
        'related_tasks': ['submit_corporation_tax_return'],
    },
    'submit_corporation_tax_return': {
        'task_name': 'File a Company Tax Return',
        'category': 'business',
        'subcategory': 'corporation_tax',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/file-company-tax-return',
        'cost_gbp': 0.00,
        'takes_time': '1-3 hours',
        'requires': ['company_number', 'accounts', 'tax_computation'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['incorrect_figures', 'late_filing_penalty', 'accounts_not_approved'],
        'official_source': 'https://www.gov.uk/file-company-tax-return',
        'last_verified': '2026-09-19',
        'is_recurring': True,
        'recurrence': 'annually within 12 months of accounting period end',
        'related_tasks': ['pay_corporation_tax', 'register_corporation_tax'],
        'commercial_needs': ['accountant'],
    },

    # --- HOME / HOUSING ---
    'update_council_tax': {
        'task_name': 'Update your council tax details',
        'category': 'home',
        'subcategory': 'council_tax',
        'authority': 'Local Council',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/council-tax',
        'cost_gbp': 0.00,
        'takes_time': 'varies by council',
        'requires': ['identity', 'address', 'move_date'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['wrong_council', 'overlapping_liability'],
        'official_source': 'https://www.gov.uk/council-tax',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_electoral_roll', 'update_vehicle_tax'],
    },
    'update_electoral_roll': {
        'task_name': 'Register to vote',
        'category': 'home',
        'subcategory': 'electoral',
        'authority': 'Electoral Commission',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/register-to-vote',
        'cost_gbp': 0.00,
        'takes_time': '2 weeks',
        'requires': ['identity', 'address', 'nationality'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['missed_deadline'],
        'official_source': 'https://www.gov.uk/register-to-vote',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_council_tax'],
    },

    # --- BENEFITS ---
    'check_benefits': {
        'task_name': 'Check what benefits you can get',
        'category': 'benefits',
        'subcategory': 'eligibility',
        'authority': 'DWP',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/browse/child-disability-family/benefits',
        'cost_gbp': 0.00,
        'takes_time': '5 minutes',
        'requires': ['identity', 'income_details', 'household_details'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/browse/child-disability-family/benefits',
        'last_verified': '2026-09-19',
        'related_tasks': ['apply_universal_credit', 'apply_pip'],
    },
    'apply_universal_credit': {
        'task_name': 'Apply for Universal Credit',
        'category': 'benefits',
        'subcategory': 'universal_credit',
        'authority': 'DWP',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/universal-credit/how-to-apply',
        'cost_gbp': 0.00,
        'takes_time': '5-8 weeks for first payment',
        'requires': ['identity', 'income_details', 'housing_costs', 'bank_details', 'health_conditions'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['ineligibility', 'deduction_sanctions', 'change_of_circumstances_not_reported'],
        'official_source': 'https://www.gov.uk/universal-credit/how-to-apply',
        'last_verified': '2026-09-19',
        'related_tasks': ['check_benefits', 'apply_pip'],
        'commercial_needs': ['budgeting_loan'],
    },
    'apply_pip': {
        'task_name': 'Apply for Personal Independence Payment',
        'category': 'benefits',
        'subcategory': 'disability',
        'authority': 'DWP',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/pip/how-to-apply',
        'cost_gbp': 0.00,
        'takes_time': '8-12 weeks',
        'requires': ['identity', 'health_conditions', 'care_needs', 'mobility_needs'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['insufficient_evidence', 'failed_assessment', 'mandatory_reconsideration_needed'],
        'official_source': 'https://www.gov.uk/pip/how-to-apply',
        'last_verified': '2026-09-19',
        'related_tasks': ['check_benefits', 'apply_universal_credit'],
        'commercial_needs': ['disability_advice'],
    },

    # --- MOVING HOUSE ---
    'moving_house_checklist': {
        'task_name': 'Update everything when you move house',
        'category': 'home',
        'subcategory': 'moving',
        'authority': 'Multiple',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/medical-records/notifying-people',
        'cost_gbp': 0.00,
        'takes_time': '1-2 weeks',
        'requires': ['old_address', 'new_address', 'move_date'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['missed_notification', 'council_tax_overlap'],
        'official_source': 'https://www.gov.uk/medical-records/notifying-people',
        'last_verified': '2026-09-19',
        'related_tasks': ['update_address', 'update_council_tax', 'update_electoral_roll'],
    },

    # --- NEW PARENT ---
    'new_baby_admin': {
        'task_name': 'Register a birth and claim child benefits',
        'category': 'family',
        'subcategory': 'new_parent',
        'authority': 'Multiple',
        'jurisdiction': 'GB',
        'cost_gbp': 11.00,
        'takes_time': '42 days to register',
        'url': 'https://www.gov.uk/child-birth-registration',
        'requires': ['identity', 'baby_details', 'parents_details', 'address'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'explicit_approval', 'retain_credentials': False,
        },
        'failure_modes': ['late_registration', 'missing_documents'],
        'official_source': 'https://www.gov.uk/child-birth-registration',
        'last_verified': '2026-09-19',
        'related_tasks': ['apply_child_benefit', 'update_council_tax'],
        'commercial_needs': ['life_insurance', 'child_savings'],
    },
    'apply_child_benefit': {
        'task_name': 'Apply for Child Benefit',
        'category': 'benefits',
        'subcategory': 'child_benefit',
        'authority': 'HMRC',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/child-benefit',
        'cost_gbp': 0.00,
        'takes_time': '6-8 weeks',
        'requires': ['identity', 'baby_birth_certificate', 'national_insurance_number', 'bank_details'],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': True,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': ['high_income_tax_charge', 'incorrect_amount'],
        'official_source': 'https://www.gov.uk/child-benefit',
        'last_verified': '2026-09-19',
        'related_tasks': ['new_baby_admin'],
    },

    # --- EMPLOYMENT ---
    'check_employment_rights': {
        'task_name': 'Check your employment rights',
        'category': 'employment',
        'subcategory': 'rights',
        'authority': 'ACAS',
        'jurisdiction': 'GB',
        'url': 'https://www.gov.uk/employment-rights-for-employees',
        'cost_gbp': 0.00,
        'takes_time': '5 minutes',
        'requires': [],
        'agent_permissions': {
            'explain': True, 'gather_requirements': True, 'prefill': False,
            'submit': False, 'payment': 'not_possible', 'retain_credentials': False,
        },
        'failure_modes': [],
        'official_source': 'https://www.gov.uk/employment-rights-for-employees',
        'last_verified': '2026-09-19',
        'related_tasks': ['check_tax_code', 'view_licence_points'],
    },
}


# ============================================================
# Build the Action Graph
# ============================================================

def build_action_graph() -> dict:
    """Build the UK action graph from collected data.
    Maps common tasks -> requirements -> official sources -> agent permissions."""
    graph = {
        'tasks': {},
        'requirements_index': {},
        'authority_index': {},
        'category_index': {},
    }

    for task_id, task_data in CURATED_TASKS.items():
        normalized = normalize_task(task_data.get('task_name', task_id), task_data)
        graph['tasks'][task_id] = normalized

        for req in normalized['requires']:
            graph['requirements_index'].setdefault(req, []).append(task_id)

        auth = normalized['authority']
        graph['authority_index'].setdefault(auth, []).append(task_id)

        cat = normalized['category']
        graph['category_index'].setdefault(cat, []).append(task_id)

    return graph


# ============================================================
# Save to disk
# ============================================================

def _save_jsonl(data: list, subdir: str, filename: str) -> str:
    """Save a list of dicts to a JSONL file under DATA_DIR."""
    out_dir = DATA_DIR / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    with open(filepath, 'w') as f:
        for record in data:
            f.write(json.dumps(record, default=str) + '\n')
    return str(filepath)


def _save_json(data: dict, subdir: str, filename: str) -> str:
    """Save a dict to a JSON file under DATA_DIR."""
    out_dir = DATA_DIR / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    return str(filepath)


# ============================================================
# Seed orchestrators
# ============================================================

def seed_govuk() -> dict:
    """Collect from GOV.UK API and save to disk."""
    print("Collecting GOV.UK services...")
    services_resp = collect_govuk_services()
    service_count = 0
    if services_resp['status'] == 'ok':
        normalized = [normalize_service(s) for s in services_resp.get('services', [])]
        _save_jsonl(normalized, 'govuk', f'services_{TODAY}.jsonl')
        service_count = len(normalized)
        print(f"  Saved {service_count} services")

    print("Collecting GOV.UK transactions...")
    tx_resp = collect_govuk_transactions()
    tx_count = 0
    if tx_resp['status'] == 'ok':
        normalized = [normalize_transaction(t) for t in tx_resp.get('transactions', [])]
        _save_jsonl(normalized, 'govuk', f'transactions_{TODAY}.jsonl')
        tx_count = len(normalized)
        print(f"  Saved {tx_count} transactions")

    return {
        'status': 'ok',
        'services': service_count,
        'transactions': tx_count,
        'collected_at': datetime.now().isoformat(),
    }


def seed_curated_tasks() -> dict:
    """Normalize and save all curated tasks."""
    print("Seeding curated UK Admin tasks...")
    tasks = []
    for task_id, task_data in CURATED_TASKS.items():
        normalized = normalize_task(task_data.get('task_name', task_id), task_data)
        normalized['task_id'] = task_id
        tasks.append(normalized)

    _save_jsonl(tasks, 'tasks', f'uk_admin_tasks_{TODAY}.jsonl')
    print(f"  Saved {len(tasks)} curated tasks")

    # Save the action graph
    graph = build_action_graph()
    _save_json(graph, 'graph', 'action_graph.json')
    print(f"  Saved action graph with {len(graph['tasks'])} tasks, {len(graph['requirements_index'])} requirements, {len(graph['authority_index'])} authorities")

    return {
        'status': 'ok',
        'curated_tasks': len(tasks),
        'graph': {
            'tasks': len(graph['tasks']),
            'requirements': len(graph['requirements_index']),
            'authorities': len(graph['authority_index']),
            'categories': len(graph['category_index']),
        },
        'collected_at': datetime.now().isoformat(),
    }


def seed_all() -> dict:
    """Run all seed collectors."""
    print("=" * 60)
    print("UK Admin Data Garden — Seeding")
    print("=" * 60)

    results = {}

    results['govuk'] = seed_govuk()
    results['curated'] = seed_curated_tasks()

    # Summary
    print("\n" + "=" * 60)
    print("Seeding Complete")
    print("=" * 60)
    print(f"GOV.UK services collected: {results['govuk'].get('services', 0)}")
    print(f"GOV.UK transactions collected: {results['govuk'].get('transactions', 0)}")
    print(f"Curated tasks: {results['curated'].get('curated_tasks', 0)}")
    print(f"Action graph: {results['curated']['graph']}")
    print(f"Data saved to: {DATA_DIR}")

    return results


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='UK Admin — Collectors')
    parser.add_argument('--seed-govuk', action='store_true', help='Collect from GOV.UK API')
    parser.add_argument('--seed-curated', action='store_true', help='Seed curated tasks only')
    parser.add_argument('--seed-all', action='store_true', help='Run all seed collectors')
    parser.add_argument('--build-graph', action='store_true', help='Build and print the action graph')
    args = parser.parse_args()

    if args.seed_govuk:
        result = seed_govuk()
        print(json.dumps(result, indent=2, default=str))
    elif args.seed_curated:
        result = seed_curated_tasks()
        print(json.dumps(result, indent=2, default=str))
    elif args.seed_all:
        result = seed_all()
        print(json.dumps(result, indent=2, default=str))
    elif args.build_graph:
        graph = build_action_graph()
        print(json.dumps({
            'tasks': len(graph['tasks']),
            'requirements': {k: len(v) for k, v in graph['requirements_index'].items()},
            'authorities': {k: len(v) for k, v in graph['authority_index'].items()},
            'categories': {k: len(v) for k, v in graph['category_index'].items()},
        }, indent=2))
    else:
        print("UK Admin — Collectors")
        print(f"Curated tasks: {len(CURATED_TASKS)}")
        print(f"Data directory: {DATA_DIR}")
        print("\nUsage:")
        print("  python -m collectors.uk_admin_collectors --seed-govuk")
        print("  python -m collectors.uk_admin_collectors --seed-curated")
        print("  python -m collectors.uk_admin_collectors --seed-all")
        print("  python -m collectors.uk_admin_collectors --build-graph")


if __name__ == '__main__':
    main()
