"""Oldham — first UK Boring place prototype.

Complete definition of Oldham Metropolitan Borough as a Place.
"""

OLDHAM = {
    "place_id": "oldham",
    "name": "Oldham Metropolitan Borough",
    "country": "England",
    "region": "North West",
    "county": "Greater Manchester",
    "district": "Oldham",
    "local_authority": "Oldham Metropolitan Borough Council",
    "la_gss_code": "E08000004",
    "constituency": "Oldham East and Saddleworth, Oldham West and Royton",
    "police_force": "Greater Manchester Police",
    "nhs_board": "NHS Oldham CCG",
    "water_company": "United Utilities",
    "transport_authority": "Transport for Greater Manchester",
    "council_url": "https://www.oldham.gov.uk",
    "population": 237000,
    "postcode_areas": ["OL"],
}

OLDHAM_SERVICES = [
    {
        "service_id": "oldham.council_tax",
        "name": "Council Tax",
        "authority": "Oldham Metropolitan Borough Council",
        "category": "council_tax",
        "url": "https://www.oldham.gov.uk/info/200198/council_tax",
        "workflows": ["oldham.council_tax.move_home", "oldham.council_tax.band_challenge"],
    },
    {
        "service_id": "oldham.waste",
        "name": "Waste and Recycling",
        "authority": "Oldham Metropolitan Borough Council",
        "category": "waste",
        "url": "https://www.oldham.gov.uk/info/200200/waste_and_recycling",
        "workflows": ["oldham.waste.missed_bin", "oldham.waste.order_bin"],
    },
    {
        "service_id": "oldham.parking",
        "name": "Parking",
        "authority": "Oldham Metropolitan Borough Council",
        "category": "parking",
        "url": "https://www.oldham.gov.uk/info/200201/parking",
        "workflows": ["oldham.parking.permit"],
    },
    {
        "service_id": "oldham.planning",
        "name": "Planning Applications",
        "authority": "Oldham Metropolitan Borough Council",
        "category": "planning",
        "url": "https://www.oldham.gov.uk/info/200202/planning",
        "workflows": [],
    },
    {
        "service_id": "oldham.electoral",
        "name": "Electoral Registration",
        "authority": "Oldham Metropolitan Borough Council",
        "category": "electoral",
        "url": "https://www.gov.uk/register-to-vote",
        "workflows": ["oldham.electoral.register"],
    },
]
