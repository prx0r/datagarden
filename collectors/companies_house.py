"""
UKGraph — Companies House Streaming Collector

Connects to Companies House Streaming API for real-time company births/deaths.
Free, requires API key from https://developer.company-information.service.gov.uk/
"""

import os
import json
import ssl
import websocket
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'room' / 'data' / 'companies_house'


def on_message(ws, message):
    """Handle incoming company data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"

    try:
        data = json.loads(message)
        record = {
            'received_at': datetime.now().isoformat(),
            'data': data,
        }
        with open(filepath, 'a') as f:
            f.write(json.dumps(record, default=str) + '\n')

        # Print summary
        event_type = data.get('event', {}).get('type', 'unknown')
        company_number = data.get('company_number', '?')
        print(f"  {event_type}: {company_number}")
    except Exception as e:
        print(f"  Error: {e}")


def on_error(ws, error):
    print(f"  Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("  Connection closed")


def on_open(ws):
    print("  Connected to Companies House stream")


def collect(api_key: str):
    """Connect to Companies House streaming API."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Starting Companies House stream...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    ws = websocket.WebSocketApp(
        'wss://stream.companieshouse.gov.uk/companies',
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=[f'Authorization: {api_key}'],
    )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def main():
    """Run collector."""
    api_key = os.environ.get('COMPANIES_HOUSE_API_KEY')
    if not api_key:
        print("Set COMPANIES_HOUSE_API_KEY in .env")
        print("Get one free at: https://developer.company-information.service.gov.uk/")
        return

    collect(api_key)


if __name__ == '__main__':
    main()
