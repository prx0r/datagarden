#!/usr/bin/env python3
"""
UK Admin — MOT History Collector

Pulls vehicle MOT history from the DVSA API.
Free API, requires key from https://register-mot-history.api.gov.uk/

Returns:
- Vehicle details (make, model, colour, year, fuel type)
- MOT test results (date, result, mileage, advisories, failures)
- MOT expiry date
- Advisory items with descriptions
- Failure items with descriptions
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, date
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'uk_admin' / 'data' / 'vehicles'
sys.path.insert(0, str(ROOT))

MOT_API_BASE = 'https://history.mot.api.gov.uk'
MOT_AUTH_URL = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

TODAY = date.today().isoformat()


def _get_api_credentials() -> dict:
    """Get MOT API credentials from environment."""
    return {
        'client_id': os.environ.get('MOT_CLIENT_ID', ''),
        'client_secret': os.environ.get('MOT_CLIENT_SECRET', ''),
        'tenant_id': os.environ.get('MOT_TENANT_ID', ''),
        'api_key': os.environ.get('MOT_API_KEY', ''),
        'scope': os.environ.get('MOT_SCOPE', 'https://tapi.dvsa.gov.uk/.default'),
    }


_token_cache = {'token': None, 'expires_at': 0}


def _get_access_token() -> str:
    """Get OAuth2 access token for MOT API. Caches for 50 minutes."""
    now = time.time()
    if _token_cache['token'] and now < _token_cache['expires_at']:
        return _token_cache['token']

    creds = _get_api_credentials()
    if not all([creds['client_id'], creds['client_secret'], creds['tenant_id']]):
        raise ValueError(
            "MOT credentials not set. Need: MOT_CLIENT_ID, MOT_CLIENT_SECRET, "
            "MOT_TENANT_ID, MOT_API_KEY in environment"
        )

    token_url = MOT_AUTH_URL.format(tenant_id=creds['tenant_id'])
    resp = requests.post(token_url, data={
        'grant_type': 'client_credentials',
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'scope': creds['scope'],
    }, timeout=30)

    resp.raise_for_status()
    data = resp.json()

    _token_cache['token'] = data['access_token']
    _token_cache['expires_at'] = now + data.get('expires_in', 3600) - 600

    return _token_cache['token']


def _api_headers() -> dict:
    """Build authorization headers for MOT API."""
    token = _get_access_token()
    creds = _get_api_credentials()
    return {
        'Authorization': f'Bearer {token}',
        'X-API-Key': creds['api_key'],
        'Accept': 'application/json',
    }


# ============================================================
# Raw Collectors
# ============================================================

def get_vehicle_details(registration: str) -> dict:
    """Get vehicle details and MOT history from DVSA API.

    Args:
        registration: UK vehicle registration number (e.g., AB12CDE)

    Returns:
        dict with status, raw vehicle data, or error info
    """
    registration = registration.strip().upper().replace(' ', '')

    try:
        headers = _api_headers()
        url = f'{MOT_API_BASE}/v1/trade/vehicles/registration/{registration}'
        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            return {
                'status': 'ok',
                'registration': registration,
                'raw': data,
                'fetched_at': datetime.now().isoformat(),
            }

        return {
            'status': 'error',
            'registration': registration,
            'http_status': resp.status_code,
            'message': resp.text[:500],
            'fetched_at': datetime.now().isoformat(),
        }

    except requests.RequestException as e:
        return {
            'status': 'error',
            'registration': registration,
            'message': str(e),
            'fetched_at': datetime.now().isoformat(),
        }


# ============================================================
# Normalizer
# ============================================================

def normalize_mot_record(raw: dict) -> dict:
    """Normalize MOT history into canonical form.

    Args:
        raw: Raw response from DVSA API (single vehicle object)

    Returns:
        Normalized vehicle dict with MOT history
    """
    registration = raw.get('registration', '').strip().upper()
    make = raw.get('make', '').upper()
    model = raw.get('model', '').upper()
    colour = raw.get('primaryColour', '').upper()
    fuel_type = raw.get('fuelType', '').upper()

    year = None
    reg_date = raw.get('registrationDate') or raw.get('firstUsedDate')
    if reg_date:
        try:
            year = int(reg_date.split('.')[0])
        except (ValueError, IndexError):
            pass

    mot_tests = raw.get('motTests', [])
    tests = []
    total_advisories = 0
    total_failures = 0

    for test in mot_tests:
        test_date = test.get('completedDate', '')
        if test_date:
            try:
                test_date = test_date.split(' ')[0].replace('.', '-')
            except Exception:
                pass

        result = (test.get('testResult', '') or '').upper()

        mileage = None
        odometer = test.get('odometerValue')
        if odometer:
            try:
                mileage = int(odometer)
            except (ValueError, TypeError):
                pass

        advisories = []
        failures = []
        rfr_items = test.get('rfrAndComments', [])

        for item in rfr_items:
            item_type = (item.get('type', '') or '').upper()
            entry = {
                'text': item.get('text', ''),
                'type': item_type,
                'dangerous': item.get('dangerous', False),
            }

            if item_type in ('ADVISORY', 'USER ENTERED'):
                advisories.append(entry)
                total_advisories += 1
            elif item_type in ('FAIL', 'MAJOR', 'DANGEROUS'):
                failures.append(entry)
                total_failures += 1
            else:
                advisories.append(entry)
                total_advisories += 1

        expiry = test.get('expiryDate')
        if expiry:
            expiry = expiry.replace('.', '-')

        tests.append({
            'date': test_date,
            'result': result,
            'mileage': mileage,
            'expiry_date': expiry,
            'test_number': test.get('motTestNumber', ''),
            'advisories': advisories,
            'failures': failures,
        })

    last_test = tests[0] if tests else {}
    last_test_date = last_test.get('date', '')
    last_test_result = last_test.get('result', '')

    mot_expiry = None
    mot_status = 'unknown'
    if tests:
        for t in tests:
            if t.get('expiry_date'):
                mot_expiry = t['expiry_date']
                break

    if mot_expiry:
        try:
            expiry_date = datetime.strptime(mot_expiry, '%Y-%m-%d').date()
            if expiry_date >= date.today():
                mot_status = 'valid'
            else:
                mot_status = 'expired'
        except ValueError:
            mot_status = 'unknown'

    return {
        'registration': registration,
        'make': make,
        'model': model,
        'colour': colour,
        'year': year,
        'fuel_type': fuel_type,
        'engine_size_cc': raw.get('engineSize'),
        'mot_expiry': mot_expiry,
        'mot_status': mot_status,
        'last_test_date': last_test_date,
        'last_test_result': last_test_result,
        'advisory_count': total_advisories,
        'failure_count': total_failures,
        'total_tests': len(tests),
        'tests': tests,
        'vehicle_id': raw.get('vehicleId', ''),
        'first_used_date': raw.get('firstUsedDate', ''),
        'registration_date': raw.get('registrationDate', ''),
        'manufacture_date': raw.get('manufactureDate', ''),
        'source': 'dvsa_mot_history',
        'observed_at': datetime.now().isoformat(),
    }


# ============================================================
# High-level Functions
# ============================================================

def check_mot_status(registration: str) -> dict:
    """Quick check: is MOT valid? When does it expire? Any advisories?

    Args:
        registration: UK vehicle registration number

    Returns:
        dict with mot_status, expiry, advisory_count, summary
    """
    result = get_vehicle_details(registration)

    if result['status'] != 'ok':
        return {
            'status': 'error',
            'registration': registration,
            'message': result.get('message', 'API error'),
        }

    vehicle = normalize_mot_record(result['raw'])

    advisories = []
    if vehicle['tests']:
        latest = vehicle['tests'][0]
        advisories = latest.get('advisories', [])

    summary_parts = [
        f"{vehicle['make']} {vehicle['model']}",
        f"MOT: {vehicle['mot_status'].upper()}",
    ]
    if vehicle['mot_expiry']:
        summary_parts.append(f"Expires: {vehicle['mot_expiry']}")
    if advisories:
        summary_parts.append(f"{len(advisories)} advisories")

    return {
        'status': 'ok',
        'registration': vehicle['registration'],
        'make': vehicle['make'],
        'model': vehicle['model'],
        'colour': vehicle['colour'],
        'year': vehicle['year'],
        'mot_status': vehicle['mot_status'],
        'mot_expiry': vehicle['mot_expiry'],
        'last_test_date': vehicle['last_test_date'],
        'last_test_result': vehicle['last_test_result'],
        'advisory_count': vehicle['advisory_count'],
        'failure_count': vehicle['failure_count'],
        'total_tests': vehicle['total_tests'],
        'latest_advisories': advisories,
        'summary': ' | '.join(summary_parts),
        'checked_at': datetime.now().isoformat(),
    }


def get_advisory_history(registration: str) -> list:
    """Get all advisory items across MOT tests.

    Args:
        registration: UK vehicle registration number

    Returns:
        List of advisory items with test date context
    """
    result = get_vehicle_details(registration)

    if result['status'] != 'ok':
        return []

    vehicle = normalize_mot_record(result['raw'])
    all_advisories = []

    for test in vehicle['tests']:
        for adv in test.get('advisories', []):
            all_advisories.append({
                'date': test['date'],
                'mileage': test['mileage'],
                'text': adv['text'],
                'type': adv['type'],
                'dangerous': adv['dangerous'],
            })

    return all_advisories


def seed_vehicles(registrations: list) -> dict:
    """Bulk seed vehicle data from registration list.

    Args:
        registrations: List of UK registration numbers

    Returns:
        dict with counts and file paths
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []

    for reg in registrations:
        reg = reg.strip().upper()
        if not reg:
            continue

        print(f"  Fetching {reg}...")
        api_result = get_vehicle_details(reg)

        if api_result['status'] == 'ok':
            normalized = normalize_mot_record(api_result['raw'])
            results.append(normalized)

            reg_file = DATA_DIR / f'{reg}.json'
            with open(reg_file, 'w') as f:
                json.dump(normalized, f, indent=2, default=str)
        else:
            errors.append({
                'registration': reg,
                'error': api_result.get('message', 'Unknown error'),
            })
            print(f"    Error: {api_result.get('message', 'Unknown')}")

        time.sleep(0.5)

    today_file = DATA_DIR / f'seed_{TODAY}.jsonl'
    with open(today_file, 'a') as f:
        for record in results:
            f.write(json.dumps(record, default=str) + '\n')

    return {
        'status': 'ok',
        'total': len(registrations),
        'success': len(results),
        'errors': len(errors),
        'error_details': errors,
        'saved_to': str(DATA_DIR),
        'seeded_at': datetime.now().isoformat(),
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='UK Admin — MOT History Collector')
    parser.add_argument('--lookup', nargs='+', metavar='REG',
                        help='Look up vehicle details by registration(s)')
    parser.add_argument('--check', nargs='+', metavar='REG',
                        help='Quick MOT status check for registration(s)')
    parser.add_argument('--advisories', metavar='REG',
                        help='Get all advisory items for a registration')
    parser.add_argument('--seed', nargs='+', metavar='REG',
                        help='Bulk seed vehicle data from registration list')
    args = parser.parse_args()

    if args.lookup:
        for reg in args.lookup:
            print(f"\n--- {reg} ---")
            result = get_vehicle_details(reg)
            if result['status'] == 'ok':
                vehicle = normalize_mot_record(result['raw'])
                print(json.dumps(vehicle, indent=2, default=str))
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")

    elif args.check:
        for reg in args.check:
            print(f"\n--- {reg} ---")
            result = check_mot_status(reg)
            print(json.dumps(result, indent=2, default=str))

    elif args.advisories:
        print(f"\n--- Advisories: {args.advisories} ---")
        advisories = get_advisory_history(args.advisories)
        print(json.dumps(advisories, indent=2, default=str))

    elif args.seed:
        print(f"\nSeeding {len(args.seed)} vehicles...")
        result = seed_vehicles(args.seed)
        print(json.dumps(result, indent=2, default=str))

    else:
        parser.print_help()
        print("\nExamples:")
        print("  python -m collectors.mot_history --lookup AB12CDE")
        print("  python -m collectors.mot_history --check AB12CDE")
        print("  python -m collectors.mot_history --advisories AB12CDE")
        print("  python -m collectors.mot_history --seed AB12CDE XY34FGH")


if __name__ == '__main__':
    main()
