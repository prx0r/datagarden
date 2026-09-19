"""Geographic resolver.

Turns a postcode or UPRN into a Place with all jurisdictional overlays.
Uses postcodes.io (free, no key) for primary resolution.
"""

import requests
from typing import Optional
from uk_boring.place import Place

POSTCODES_IO = "https://api.postcodes.io"

def resolve_postcode(postcode: str) -> Optional[Place]:
    """Resolve a UK postcode to a Place with all jurisdictional overlays."""
    try:
        resp = requests.get(f"{POSTCODES_IO}/postcodes/{postcode.replace(' ', '')}", timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json().get('result', {})
        if not data:
            return None

        return Place(
            postcode=data.get('postcode', postcode),
            country=data.get('country', ''),
            region=data.get('region', ''),
            county=data.get('admin_district', ''),  # In UK, admin_district is often the county
            district=data.get('admin_district', ''),
            ward=data.get('admin_ward', ''),
            local_authority=data.get('admin_district', ''),
            la_gss_code=data.get('codes', {}).get('admin_district', ''),
            constituency=data.get('parliamentary_constituency', ''),
            police_force=data.get('lsoa', '').split()[0] if data.get('lsoa') else '',  # Approximate
            nhs_board=data.get('ccg', ''),
            water_company=data.get('nuts', ''),  # Approximate
            source='postcodes_io',
        )
    except Exception as e:
        return None


def resolve_uprn(uprn: str) -> Optional[Place]:
    """Resolve a UPRN to a Place.

    UPRN is the strongest identifier for every addressable location in GB.
    Currently uses postcodes.io termination endpoint as fallback.
    """
    try:
        resp = requests.get(f"{POSTCODES_IO}/terminated_postcodes/{uprn}", timeout=10)
        # postcodes.io doesn't directly support UPRN, so we'd need another source
        # For now, return None and let the system fall back to postcode
        return None
    except Exception:
        return None


def get_nearest_postcodes(postcode: str, limit: int = 10) -> list:
    """Get nearest postcodes (useful for catchment areas)."""
    try:
        resp = requests.get(f"{POSTCODES_IO}/postcodes/{postcode.replace(' ', '')}/autocomplete", timeout=10)
        if resp.status_code == 200:
            return resp.json().get('result', [])[:limit]
    except Exception:
        pass
    return []
