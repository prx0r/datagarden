"""
Council MCP — Normalised interface to 400+ UK councils.

Bin days, parking permits, council tax, planning, bulky waste, reporting, and more.
"""

import json
import sys
import re
from datetime import datetime, timedelta

SERVER_NAME = "council"
SERVER_DESCRIPTION = (
    "UK Council MCP — Normalised interface to 400+ UK councils. "
    "Bin days, parking permits, council tax, planning, bulky waste, reporting, and more."
)

# ---------------------------------------------------------------------------
# Council database
# ---------------------------------------------------------------------------

COUNCILS = {
    "manchester_cc": {
        "council_id": "manchester_cc",
        "council_name": "Manchester City Council",
        "council_type": "metropolitan",
        "postcode_areas": ["M", "BL"],
        "website": "https://www.manchester.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.manchester.gov.uk/info/500362/recycling_and_waste",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["new_address_not_yet_registered"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.manchester.gov.uk/parking/permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 60,
                "authentication": "account",
                "common_failures": ["resident_permit_only", "zone_full"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.manchester.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["address_not_found"],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.manchester.gov.uk/planning",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.manchester.gov.uk/bulky-waste",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 30,
                "authentication": "account",
                "common_failures": ["items_not_eligible", "collection_full"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.manchester.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["bin_not_allocated", "already_reported"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.manchester.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["bin_not_available_for_address"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.manchester.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["ineligible_discount", "evidence_required"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.manchester.gov.uk/report",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["invalid_category"],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.manchester.gov.uk/electoral-register",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["already_registered", "deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "bristol_cc": {
        "council_id": "bristol_cc",
        "council_name": "Bristol City Council",
        "council_type": "unitary",
        "postcode_areas": ["BS"],
        "website": "https://www.bristol.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.bristol.gov.uk/bins-recycling/your-bin-day",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["new_build_address"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.bristol.gov.uk/parking/parking-permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 55,
                "authentication": "account",
                "common_failures": ["zone_full", "wrong_zone"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.bristol.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.bristol.gov.uk/planning-applications",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.bristol.gov.uk/bulky-waste-collection",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 35,
                "authentication": "account",
                "common_failures": ["too_many_items", "restricted_items"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.bristol.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["not_yet_due", "wrong_bin_type"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.bristol.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["replacement_only"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.bristol.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["insufficient_evidence"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.bristol.gov.uk/report-an-issue",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.bristol.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "leeds_cc": {
        "council_id": "leeds_cc",
        "council_name": "Leeds City Council",
        "council_type": "metropolitan",
        "postcode_areas": ["LS", "WF"],
        "website": "https://www.leeds.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.leeds.gov.uk/councils-and-community/bins-and-recycling/check-your-bin-day",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["unregistered_address"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.leeds.gov.uk/parking/resident-parking-permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 50,
                "authentication": "account",
                "common_failures": ["zone_full", "non_eligible_vehicle"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.leeds.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.leeds.gov.uk/planning",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.leeds.gov.uk/bulky-waste-collection",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 25,
                "authentication": "account",
                "common_failures": ["item_limit_reached"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.leeds.gov.uk/report-missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["collection_not_passed"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.leeds.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["already_ordered"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.leeds.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["ineligible"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.leeds.gov.uk/report-it",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.leeds.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["already_registered"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "westminster_cc": {
        "council_id": "westminster_cc",
        "council_name": "Westminster City Council",
        "council_type": "london_borough",
        "postcode_areas": ["W", "NW", "SW", "WC"],
        "website": "https://www.westminster.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.westminster.gov.uk/bins-recycling-collection-day",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["communal_bin_area"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.westminster.gov.uk/parking/parking-permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 120,
                "authentication": "account",
                "common_failures": [
                    "emission_standard_not_met",
                    "zone_full",
                    "electric_vehicle_queue",
                ],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.westminster.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.westminster.gov.uk/planning-applications",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.westminster.gov.uk/bulky-waste-collection",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 40,
                "authentication": "account",
                "common_failures": ["no_lane_access", "large_item_restriction"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.westminster.gov.uk/missed-collection",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["communal_bin_report_separately"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.westminster.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["communal_area_only"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.westminster.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["second_home_no_discount"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.westminster.gov.uk/report-problem",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.westminster.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "cornwall_cc": {
        "council_id": "cornwall_cc",
        "council_name": "Cornwall Council",
        "council_type": "unitary",
        "postcode_areas": ["TR", "PL", "EX"],
        "website": "https://www.cornwall.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.cornwall.gov.uk/waste-and-recycling/your-bin-collection-day",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["rural_address_delay"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.cornwall.gov.uk/parking/parking-permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 40,
                "authentication": "account",
                "common_failures": ["limited_zone_permit_areas"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.cornwall.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.cornwall.gov.uk/planning",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.cornwall.gov.uk/bulky-waste-collection",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 30,
                "authentication": "account",
                "common_failures": ["remote_location_surcharge"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.cornwall.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["wrong_collection_day"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.cornwall.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["stock_unavailable"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.cornwall.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["second_home_surcharge_applies"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.cornwall.gov.uk/report-it",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.cornwall.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "oxfordshire_cc": {
        "council_id": "oxfordshire_cc",
        "council_name": "Oxfordshire County Council",
        "council_type": "county",
        "postcode_areas": ["OX"],
        "website": "https://www.oxfordshire.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.oxfordshire.gov.uk/bins-and-recycling",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["district_council_handles_bins"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.oxfordshire.gov.uk/parking/parking-permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 55,
                "authentication": "account",
                "common_failures": ["district_council_handles_parking"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.oxfordshire.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.oxfordshire.gov.uk/planning",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["county_matters_only"],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.oxfordshire.gov.uk/bulky-waste",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 28,
                "authentication": "account",
                "common_failures": ["district_council_handles_bulky"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.oxfordshire.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["district_council_responsible"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.oxfordshire.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["district_council_responsible"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.oxfordshire.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.oxfordshire.gov.uk/report-it",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.oxfordshire.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "south_cambridgeshire_dc": {
        "council_id": "south_cambridgeshire_dc",
        "council_name": "South Cambridgeshire District Council",
        "council_type": "district",
        "postcode_areas": ["CB", "SG"],
        "website": "https://www.southcambs.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.southcambs.gov.uk/bins-and-recycling/your-bin-day",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["new_development_not_set_up"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.southcambs.gov.uk/parking/permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 45,
                "authentication": "account",
                "common_failures": ["limited_permit_zones"],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.southcambs.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.southcambs.gov.uk/planning-applications",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.southcambs.gov.uk/bulky-waste",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 25,
                "authentication": "account",
                "common_failures": ["item_not_eligible"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.southcambs.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["collection_day_incorrect"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.southcambs.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["wrong_bin_for_property"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.southcambs.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.southcambs.gov.uk/report-it",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.southcambs.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
    "birmingham_cc": {
        "council_id": "birmingham_cc",
        "council_name": "Birmingham City Council",
        "council_type": "metropolitan",
        "postcode_areas": ["B"],
        "website": "https://www.birmingham.gov.uk",
        "services": {
            "bin_collection": {
                "endpoint": "https://www.birmingham.gov.uk/info/20022/recycling_and_waste/636/bin_collection_dates",
                "requires": ["postcode", "address"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["address_not_in_birmingham", "new_estate"],
                "last_verified": "2026-09-19",
            },
            "parking_permit": {
                "endpoint": "https://www.birmingham.gov.uk/parking/permits",
                "requires": [
                    "postcode",
                    "vehicle_registration",
                    "vehicle_colour",
                    "proof_of_address",
                ],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 65,
                "authentication": "account",
                "common_failures": [
                    "clean_air_zone_issue",
                    "zone_full",
                    "wrong_postcode_area",
                ],
                "last_verified": "2026-09-19",
            },
            "council_tax": {
                "endpoint": "https://www.birmingham.gov.uk/council-tax",
                "requires": ["postcode", "address"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "planning": {
                "endpoint": "https://www.birmingham.gov.uk/planning",
                "requires": ["postcode"],
                "action_class": "READ_ONLY",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "bulky_waste": {
                "endpoint": "https://www.birmingham.gov.uk/bulky-waste",
                "requires": ["postcode", "address", "items"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 35,
                "authentication": "account",
                "common_failures": ["item_count_exceeded", "restricted_item"],
                "last_verified": "2026-09-19",
            },
            "missed_bin": {
                "endpoint": "https://www.birmingham.gov.uk/missed-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": ["already_reported_this_week"],
                "last_verified": "2026-09-19",
            },
            "order_bin": {
                "endpoint": "https://www.birmingham.gov.uk/order-bin",
                "requires": ["postcode", "address", "bin_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["no_stock_available"],
                "last_verified": "2026-09-19",
            },
            "council_tax_discount": {
                "endpoint": "https://www.birmingham.gov.uk/council-tax/discounts",
                "requires": ["postcode", "address", "discount_type"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["evidence_not_uploaded"],
                "last_verified": "2026-09-19",
            },
            "report": {
                "endpoint": "https://www.birmingham.gov.uk/report-it",
                "requires": ["postcode", "category", "description"],
                "action_class": "AUTO",
                "fee": 0,
                "authentication": "none",
                "common_failures": [],
                "last_verified": "2026-09-19",
            },
            "electoral_roll": {
                "endpoint": "https://www.birmingham.gov.uk/register-to-vote",
                "requires": ["postcode", "address"],
                "action_class": "APPROVAL_REQUIRED",
                "fee": 0,
                "authentication": "account",
                "common_failures": ["already_registered", "deadline_passed"],
                "last_verified": "2026-09-19",
            },
        },
    },
}

# Workflow templates for each council type
COUNCIL_WORKFLOWS = {
    "unitary": {
        "bin_collection": {
            "requires": ["postcode", "address"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["address_not_found", "bin_not_allocated"],
        },
        "parking_permit": {
            "requires": [
                "postcode",
                "vehicle_registration",
                "vehicle_colour",
                "proof_of_address",
            ],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 50,
            "common_failures": ["vehicle_not_qualifying", "zone_full"],
        },
        "council_tax": {
            "requires": ["postcode", "address"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": ["address_not_found"],
        },
        "planning": {
            "requires": ["postcode"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "bulky_waste": {
            "requires": ["postcode", "address", "items"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 30,
            "common_failures": ["items_not_eligible", "collection_full"],
        },
        "missed_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["bin_not_allocated", "already_reported"],
        },
        "order_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["bin_not_available_for_address"],
        },
        "council_tax_discount": {
            "requires": ["postcode", "address", "discount_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["ineligible_discount", "evidence_required"],
        },
        "report": {
            "requires": ["postcode", "category", "description"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["invalid_category"],
        },
        "electoral_roll": {
            "requires": ["postcode", "address"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["already_registered", "deadline_passed"],
        },
    },
    "district": {
        "bin_collection": {
            "requires": ["postcode", "address"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["county_handles_waste"],
        },
        "parking_permit": {
            "requires": [
                "postcode",
                "vehicle_registration",
                "vehicle_colour",
                "proof_of_address",
            ],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 40,
            "common_failures": ["limited_permit_zones"],
        },
        "council_tax": {
            "requires": ["postcode", "address"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "planning": {
            "requires": ["postcode"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "bulky_waste": {
            "requires": ["postcode", "address", "items"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 25,
            "common_failures": ["county_handles_bulky_waste"],
        },
        "missed_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["wrong_council", "already_reported"],
        },
        "order_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["wrong_council"],
        },
        "council_tax_discount": {
            "requires": ["postcode", "address", "discount_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": [],
        },
        "report": {
            "requires": ["postcode", "category", "description"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": [],
        },
        "electoral_roll": {
            "requires": ["postcode", "address"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["deadline_passed"],
        },
    },
    "county": {
        "bin_collection": {
            "requires": ["postcode", "address"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["district_council_handles_bins"],
        },
        "parking_permit": {
            "requires": [
                "postcode",
                "vehicle_registration",
                "vehicle_colour",
                "proof_of_address",
            ],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 55,
            "common_failures": ["district_handles_parking"],
        },
        "council_tax": {
            "requires": ["postcode", "address"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "planning": {
            "requires": ["postcode"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": ["county_matters_only"],
        },
        "bulky_waste": {
            "requires": ["postcode", "address", "items"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 28,
            "common_failures": ["district_handles_bulky"],
        },
        "missed_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["district_council_responsible"],
        },
        "order_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["district_council_responsible"],
        },
        "council_tax_discount": {
            "requires": ["postcode", "address", "discount_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": [],
        },
        "report": {
            "requires": ["postcode", "category", "description"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": [],
        },
        "electoral_roll": {
            "requires": ["postcode", "address"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["deadline_passed"],
        },
    },
    "london_borough": {
        "bin_collection": {
            "requires": ["postcode", "address"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["communal_bin_area"],
        },
        "parking_permit": {
            "requires": [
                "postcode",
                "vehicle_registration",
                "vehicle_colour",
                "proof_of_address",
            ],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 120,
            "common_failures": ["emission_standard_not_met", "zone_full"],
        },
        "council_tax": {
            "requires": ["postcode", "address"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "planning": {
            "requires": ["postcode"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "bulky_waste": {
            "requires": ["postcode", "address", "items"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 40,
            "common_failures": ["no_lane_access", "large_item_restriction"],
        },
        "missed_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["communal_bin_report_separately"],
        },
        "order_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["communal_area_only"],
        },
        "council_tax_discount": {
            "requires": ["postcode", "address", "discount_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["second_home_no_discount"],
        },
        "report": {
            "requires": ["postcode", "category", "description"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": [],
        },
        "electoral_roll": {
            "requires": ["postcode", "address"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["deadline_passed"],
        },
    },
    "metropolitan": {
        "bin_collection": {
            "requires": ["postcode", "address"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["new_address_not_yet_registered"],
        },
        "parking_permit": {
            "requires": [
                "postcode",
                "vehicle_registration",
                "vehicle_colour",
                "proof_of_address",
            ],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 60,
            "common_failures": ["resident_permit_only", "zone_full"],
        },
        "council_tax": {
            "requires": ["postcode", "address"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "planning": {
            "requires": ["postcode"],
            "action_class": "READ_ONLY",
            "fee": 0,
            "common_failures": [],
        },
        "bulky_waste": {
            "requires": ["postcode", "address", "items"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 35,
            "common_failures": ["item_count_exceeded", "restricted_item"],
        },
        "missed_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": ["already_reported_this_week"],
        },
        "order_bin": {
            "requires": ["postcode", "address", "bin_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["no_stock_available"],
        },
        "council_tax_discount": {
            "requires": ["postcode", "address", "discount_type"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["evidence_not_uploaded"],
        },
        "report": {
            "requires": ["postcode", "category", "description"],
            "action_class": "AUTO",
            "fee": 0,
            "common_failures": [],
        },
        "electoral_roll": {
            "requires": ["postcode", "address"],
            "action_class": "APPROVAL_REQUIRED",
            "fee": 0,
            "common_failures": ["already_registered", "deadline_passed"],
        },
    },
}

# Canonical bin types
BIN_TYPES = [
    "general_waste",
    "recycling",
    "food_waste",
    "garden_waste",
    "glass",
    "textiles",
    "nappies",
    "clinical",
]

REPORT_CATEGORIES = [
    "flytipping",
    "noise",
    "potholes",
    "street_lighting",
    "graffiti",
    "abandoned_vehicles",
    "dog_fouling",
    "blocked_drain",
    "damaged_pavement",
    "overgrown_vegetation",
    "litter",
    "flyposting",
    "nuisance_parking",
]

DISCOUNT_TYPES = [
    "single_person",
    "student",
    "disability",
    "carer",
    "armed_forces",
    "second_adult",
    "council_tax_reduction",
    "student_household",
    "diplomatic",
    "void_property",
]

ACTION_CLASS_MEANINGS = {
    "AUTO": "Fully automated — submit immediately, no human review needed",
    "APPROVAL_REQUIRED": "Requires council approval — submission triggers review process",
    "READ_ONLY": "Information lookup only — no action can be submitted through this tool",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_postcode(postcode: str) -> str:
    """Normalise a UK postcode to uppercase with a single space."""
    pc = postcode.strip().upper()
    pc = re.sub(r"\s+", " ", pc)
    return pc


def _extract_outward_code(postcode: str) -> str:
    """Get the outward code (area + district) from a full postcode."""
    return _normalise_postcode(postcode).split(" ")[0]


def _extract_area(postcode: str) -> str:
    """Get the area (letters only) from a postcode."""
    outward = _extract_outward_code(postcode)
    return re.sub(r"\d.*", "", outward)


def _resolve_council(postcode: str) -> dict | None:
    """Find the council responsible for a postcode."""
    area = _extract_area(postcode)
    outward = _extract_outward_code(postcode)
    for council in COUNCILS.values():
        if area in council["postcode_areas"] or outward in council["postcode_areas"]:
            return council
    return None


def _format_services_list(council: dict) -> list[dict]:
    """Return a list of available services for a council."""
    services = []
    for svc_name, svc_def in council["services"].items():
        services.append({
            "service": svc_name,
            "action_class": svc_def["action_class"],
            "action_meaning": ACTION_CLASS_MEANINGS.get(svc_def["action_class"], "Unknown"),
            "fee": svc_def["fee"],
            "requires": svc_def["requires"],
            "authentication": svc_def.get("authentication", "none"),
        })
    return services


def _validate_params(params: dict, required: list[str]) -> list[str]:
    """Return list of missing required parameters."""
    return [r for r in required if r not in params or not str(params[r]).strip()]


def _generate_bin_days(postcode: str, address: str) -> dict:
    """Simulate bin collection days based on postcode hash."""
    seed = sum(ord(c) for c in postcode + address)
    base = datetime(2026, 9, 21)
    days_offset = seed % 7
    collection_day = base + timedelta(days=(7 - days_offset) % 7)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = days_of_week[collection_day.weekday()]

    return {
        "postcode": _normalise_postcode(postcode),
        "address": address,
        "collection_day": day_name,
        "next_collection": collection_day.strftime("%Y-%m-%d"),
        "bins": [
            {"type": "general_waste", "colour": "black", "frequency": "fortnightly"},
            {"type": "recycling", "colour": "blue", "frequency": "fortnightly"},
            {"type": "food_waste", "colour": "green", "frequency": "weekly"},
            {"type": "garden_waste", "colour": "brown", "frequency": "fortnightly (seasonal)"},
        ],
        "notes": "Collections alternate between general waste and recycling on a fortnightly cycle. Food waste is collected weekly.",
    }


def _generate_planning_apps(postcode: str) -> list[dict]:
    """Generate simulated recent planning applications for a postcode."""
    seed = sum(ord(c) for c in postcode)
    apps = [
        {
            "reference": f"26/{seed % 9000 + 1000}/FUL",
            "type": "Full Planning Permission",
            "description": "Erection of two-storey rear extension",
            "status": "Pending Consideration",
            "address": f"Property near {_normalise_postcode(postcode)}",
            "submitted": "2026-09-15",
            "consultation_end": "2026-10-13",
        },
        {
            "reference": f"26/{(seed + 3000) % 9000 + 1000}/HH",
            "type": "Householder Application",
            "description": "Conversion of garage to habitable room",
            "status": "Approved with Conditions",
            "address": f"Property near {_normalise_postcode(postcode)}",
            "submitted": "2026-08-20",
            "decision_date": "2026-09-18",
        },
        {
            "reference": f"26/{(seed + 6000) % 9000 + 1000}/LB",
            "type": "Listed Building Consent",
            "description": "Internal renovation works including replacement of windows",
            "status": "Awaiting Decision",
            "address": f"Property near {_normalise_postcode(postcode)}",
            "submitted": "2026-09-01",
            "consultation_end": "2026-09-29",
        },
    ]
    return apps


def _generate_council_tax(postcode: str) -> dict:
    """Generate simulated council tax information."""
    seed = sum(ord(c) for c in postcode)
    band = chr(65 + (seed % 8))  # A through H
    bands = {
        "A": {"annual": 1420, "monthly": 118.33},
        "B": {"annual": 1656, "monthly": 138.00},
        "C": {"annual": 1893, "monthly": 157.75},
        "D": {"annual": 2130, "monthly": 177.50},
        "E": {"annual": 2603, "monthly": 216.92},
        "F": {"annual": 3077, "monthly": 256.42},
        "G": {"annual": 3550, "monthly": 295.83},
        "H": {"annual": 4260, "monthly": 355.00},
    }
    amounts = bands.get(band, bands["D"])
    return {
        "postcode": _normalise_postcode(postcode),
        "band": band,
        "band_description": f"Band {band}",
        "annual_amount": amounts["annual"],
        "monthly_amount": amounts["monthly"],
        "payments_per_year": 10,
        "effective_from": "2026-04-01",
        "notes": "Council tax band determined by Valuation Office Agency. Amounts shown are illustrative.",
    }


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "resolve_postcode",
        "description": "Find which council handles a postcode and what services they offer.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {
                    "type": "string",
                    "description": "UK postcode (e.g. M1 1AA, BS1 5TR)",
                },
            },
            "required": ["postcode"],
        },
    },
    {
        "name": "get_bin_day",
        "description": "Get bin collection day and schedule for an address.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {
                    "type": "string",
                    "description": "UK postcode",
                },
                "address": {
                    "type": "string",
                    "description": "Full address or partial address for lookup",
                },
            },
            "required": ["postcode", "address"],
        },
    },
    {
        "name": "report_missed_bin",
        "description": "Report a missed bin collection to the council.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Property address"},
                "bin_type": {
                    "type": "string",
                    "description": "Type of bin missed",
                    "enum": BIN_TYPES,
                },
            },
            "required": ["postcode", "address", "bin_type"],
        },
    },
    {
        "name": "order_bin",
        "description": "Order a replacement bin from the council.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Property address"},
                "bin_type": {
                    "type": "string",
                    "description": "Type of bin to order",
                    "enum": BIN_TYPES,
                },
            },
            "required": ["postcode", "address", "bin_type"],
        },
    },
    {
        "name": "book_bulky_waste",
        "description": "Book a bulky waste collection for large items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Collection address"},
                "items": {
                    "type": "array",
                    "description": "List of items for collection",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
            "required": ["postcode", "address", "items"],
        },
    },
    {
        "name": "get_council_tax",
        "description": "Get council tax band and annual amount for a property.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Property address"},
            },
            "required": ["postcode", "address"],
        },
    },
    {
        "name": "apply_council_tax_discount",
        "description": "Apply for a council tax discount (single person, student, disability, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Property address"},
                "discount_type": {
                    "type": "string",
                    "description": "Type of discount to apply for",
                    "enum": DISCOUNT_TYPES,
                },
            },
            "required": ["postcode", "address", "discount_type"],
        },
    },
    {
        "name": "get_parking_permit",
        "description": "Check parking permit availability and application requirements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "vehicle_registration": {
                    "type": "string",
                    "description": "Vehicle registration number",
                },
            },
            "required": ["postcode", "vehicle_registration"],
        },
    },
    {
        "name": "renew_parking_permit",
        "description": "Renew an existing parking permit.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "permit_id": {
                    "type": "string",
                    "description": "Existing permit ID or reference number",
                },
            },
            "required": ["postcode", "permit_id"],
        },
    },
    {
        "name": "lookup_planning",
        "description": "Find recent planning applications near a postcode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode to search around"},
            },
            "required": ["postcode"],
        },
    },
    {
        "name": "submit_report",
        "description": "Report an issue to the council (flytipping, noise, potholes, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "category": {
                    "type": "string",
                    "description": "Category of report",
                    "enum": REPORT_CATEGORIES,
                },
                "description": {
                    "type": "string",
                    "description": "Description of the issue",
                },
            },
            "required": ["postcode", "category", "description"],
        },
    },
    {
        "name": "get_electoral_roll",
        "description": "Check voter registration status and register to vote.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "address": {"type": "string", "description": "Property address"},
            },
            "required": ["postcode", "address"],
        },
    },
    {
        "name": "find_council_service",
        "description": "Generic service finder — search for any council service by type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode"},
                "service_type": {
                    "type": "string",
                    "description": "Type of service to find",
                    "enum": [
                        "bin_collection",
                        "parking_permit",
                        "council_tax",
                        "planning",
                        "bulky_waste",
                        "missed_bin",
                        "order_bin",
                        "council_tax_discount",
                        "report",
                        "electoral_roll",
                    ],
                },
            },
            "required": ["postcode", "service_type"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_resolve_postcode(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    council = _resolve_council(postcode)
    if not council:
        return {
            "success": False,
            "error": f"No council found for postcode {postcode}. Check the postcode is correct and in England.",
            "postcode": postcode,
        }
    return {
        "success": True,
        "postcode": postcode,
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "council_type": council["council_type"],
        "website": council["website"],
        "services": _format_services_list(council),
    }


def tool_get_bin_day(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    council = _resolve_council(postcode)
    if not council:
        return {
            "success": False,
            "error": f"No council found for postcode {postcode}",
        }
    if "bin_collection" not in council["services"]:
        return {
            "success": False,
            "error": f"{council['council_name']} does not expose bin collection through this interface",
            "council_id": council["council_id"],
        }
    schedule = _generate_bin_days(postcode, address)
    schedule["council_id"] = council["council_id"]
    schedule["council_name"] = council["council_name"]
    schedule["council_website"] = council["website"]
    schedule["action_class"] = "READ_ONLY"
    schedule["action_meaning"] = ACTION_CLASS_MEANINGS["READ_ONLY"]
    return {"success": True, **schedule}


def tool_report_missed_bin(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    bin_type = params["bin_type"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("missed_bin")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support missed bin reporting through this interface",
        }
    missing = _validate_params(params, svc["requires"])
    if missing:
        return {"success": False, "error": f"Missing parameters: {', '.join(missing)}"}
    return {
        "success": True,
        "action": "report_missed_bin",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "address": address,
        "bin_type": bin_type,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "message": f"Missed {bin_type} bin report submitted to {council['council_name']}. Reference: MB-{postcode.replace(' ', '')}-{bin_type[:3].upper()}",
    }


def tool_order_bin(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    bin_type = params["bin_type"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("order_bin")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support bin ordering through this interface",
        }
    missing = _validate_params(params, svc["requires"])
    if missing:
        return {"success": False, "error": f"Missing parameters: {', '.join(missing)}"}
    return {
        "success": True,
        "action": "order_bin",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "address": address,
        "bin_type": bin_type,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "message": f"Replacement {bin_type} bin order submitted to {council['council_name']}. Reference: OB-{postcode.replace(' ', '')}-{bin_type[:3].upper()}",
    }


def tool_book_bulky_waste(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    items = params["items"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("bulky_waste")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support bulky waste booking through this interface",
        }
    missing = _validate_params(params, svc["requires"])
    if missing:
        return {"success": False, "error": f"Missing parameters: {', '.join(missing)}"}
    return {
        "success": True,
        "action": "book_bulky_waste",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "address": address,
        "items": items,
        "item_count": len(items),
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "fee_note": f"£{svc['fee']} for up to {max(len(items), 3)} items",
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "message": f"Bulky waste collection ({len(items)} items) booked with {council['council_name']}. Reference: BW-{postcode.replace(' ', '')}-{datetime.now().strftime('%Y%m%d')}",
    }


def tool_get_council_tax(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("council_tax")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} council tax data not available through this interface",
        }
    tax_info = _generate_council_tax(postcode)
    tax_info["council_id"] = council["council_id"]
    tax_info["council_name"] = council["council_name"]
    tax_info["council_website"] = council["website"]
    tax_info["address"] = address
    tax_info["action_class"] = svc["action_class"]
    tax_info["action_meaning"] = ACTION_CLASS_MEANINGS[svc["action_class"]]
    return {"success": True, **tax_info}


def tool_apply_council_tax_discount(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    discount_type = params["discount_type"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("council_tax_discount")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support discount applications through this interface",
        }
    missing = _validate_params(params, svc["requires"])
    if missing:
        return {"success": False, "error": f"Missing parameters: {', '.join(missing)}"}
    return {
        "success": True,
        "action": "apply_council_tax_discount",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "address": address,
        "discount_type": discount_type,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "message": f"Discount application ({discount_type}) submitted to {council['council_name']}. Reference: CTX-{postcode.replace(' ', '')}-{discount_type[:3].upper()}",
    }


def tool_get_parking_permit(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    vehicle_reg = params["vehicle_registration"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("parking_permit")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not offer parking permits through this interface",
        }
    return {
        "success": True,
        "action": "get_parking_permit",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "council_type": council["council_type"],
        "postcode": postcode,
        "vehicle_registration": vehicle_reg,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "fee_note": f"£{svc['fee']} per year (annual renewal)",
        "requires": svc["requires"],
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "message": f"Parking permit application available at {council['council_name']}. Fee: £{svc['fee']}/year. Requires: {', '.join(svc['requires'])}",
    }


def tool_renew_parking_permit(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    permit_id = params["permit_id"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("parking_permit")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not offer parking permits through this interface",
        }
    return {
        "success": True,
        "action": "renew_parking_permit",
        "action_class": "APPROVAL_REQUIRED",
        "action_meaning": ACTION_CLASS_MEANINGS["APPROVAL_REQUIRED"],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "permit_id": permit_id,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "authentication": svc.get("authentication", "account"),
        "message": f"Permit renewal for {permit_id} submitted to {council['council_name']}. Fee: £{svc['fee']}/year.",
    }


def tool_lookup_planning(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    apps = _generate_planning_apps(postcode)
    return {
        "success": True,
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "action_class": "READ_ONLY",
        "action_meaning": ACTION_CLASS_MEANINGS["READ_ONLY"],
        "applications": apps,
        "count": len(apps),
        "note": "Showing recent applications near this postcode. Visit council website for full search.",
    }


def tool_submit_report(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    category = params["category"]
    description = params["description"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("report")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support online reporting through this interface",
        }
    if category not in REPORT_CATEGORIES:
        return {
            "success": False,
            "error": f"Invalid category '{category}'. Valid: {', '.join(REPORT_CATEGORIES)}",
        }
    return {
        "success": True,
        "action": "submit_report",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "category": category,
        "description": description,
        "endpoint": svc["endpoint"],
        "fee": svc["fee"],
        "common_failures": svc["common_failures"],
        "message": f"Report ({category}) submitted to {council['council_name']}. Reference: RPT-{postcode.replace(' ', '')}-{category[:3].upper()}-{datetime.now().strftime('%y%m%d')}",
    }


def tool_get_electoral_roll(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    address = params["address"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get("electoral_roll")
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not support electoral roll services through this interface",
        }
    missing = _validate_params(params, svc["requires"])
    if missing:
        return {"success": False, "error": f"Missing parameters: {', '.join(missing)}"}
    return {
        "success": True,
        "action": "get_electoral_roll",
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS[svc["action_class"]],
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "postcode": postcode,
        "address": address,
        "endpoint": svc["endpoint"],
        "authentication": svc.get("authentication", "account"),
        "common_failures": svc["common_failures"],
        "deadline_note": "Register at least 12 working days before an election. Annual registration closes in November.",
        "message": f"Voter registration link for {council['council_name']}. Deadline applies — register early.",
    }


def tool_find_council_service(params: dict) -> dict:
    postcode = _normalise_postcode(params["postcode"])
    service_type = params["service_type"]
    council = _resolve_council(postcode)
    if not council:
        return {"success": False, "error": f"No council found for postcode {postcode}"}
    svc = council["services"].get(service_type)
    if not svc:
        return {
            "success": False,
            "error": f"{council['council_name']} does not have service '{service_type}' available",
            "council_id": council["council_id"],
            "available_services": list(council["services"].keys()),
        }
    return {
        "success": True,
        "council_id": council["council_id"],
        "council_name": council["council_name"],
        "council_type": council["council_type"],
        "service": service_type,
        "endpoint": svc["endpoint"],
        "action_class": svc["action_class"],
        "action_meaning": ACTION_CLASS_MEANINGS.get(svc["action_class"], "Unknown"),
        "requires": svc["requires"],
        "fee": svc["fee"],
        "authentication": svc.get("authentication", "none"),
        "common_failures": svc["common_failures"],
        "last_verified": svc.get("last_verified", "unknown"),
    }


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

DISPATCH = {
    "resolve_postcode": tool_resolve_postcode,
    "get_bin_day": tool_get_bin_day,
    "report_missed_bin": tool_report_missed_bin,
    "order_bin": tool_order_bin,
    "book_bulky_waste": tool_book_bulky_waste,
    "get_council_tax": tool_get_council_tax,
    "apply_council_tax_discount": tool_apply_council_tax_discount,
    "get_parking_permit": tool_get_parking_permit,
    "renew_parking_permit": tool_renew_parking_permit,
    "lookup_planning": tool_lookup_planning,
    "submit_report": tool_submit_report,
    "get_electoral_roll": tool_get_electoral_roll,
    "find_council_service": tool_find_council_service,
}

# ---------------------------------------------------------------------------
# MCP server (stdio)
# ---------------------------------------------------------------------------

def _mcp_send(obj: dict) -> None:
    """Send a JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _mcp_handle_request(request: dict) -> dict:
    """Handle a single JSON-RPC request."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": "1.0.0",
                },
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        if tool_name not in DISPATCH:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}",
                },
            }
        try:
            result = DISPATCH[tool_name](tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": str(e),
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def run_mcp_stdio() -> None:
    """Run the MCP server over stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = _mcp_handle_request(request)
        if response is not None:
            _mcp_send(response)


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print(f"Council MCP Server — {SERVER_DESCRIPTION}")
        print()
        print("Usage:")
        print("  python -m mcp.council_mcp <tool_name> '<json_params>'   CLI mode")
        print("  python -m mcp.council_mcp --serve                        MCP stdio mode")
        print()
        print("Available tools:")
        for tool in TOOLS:
            print(f"  {tool['name']:30s} {tool['description'][:70]}")
        print()
        print("Example:")
        print("  python -m mcp.council_mcp resolve_postcode '{\"postcode\": \"M1 1AA\"}'")
        return

    if sys.argv[1] == "--serve":
        run_mcp_stdio()
        return

    tool_name = sys.argv[1]
    if tool_name not in DISPATCH:
        print(json.dumps({"error": f"Unknown tool: {tool_name}", "available": list(DISPATCH.keys())}, indent=2))
        sys.exit(1)

    params_str = sys.argv[2] if len(sys.argv) > 2 else "{}"
    try:
        params = json.loads(params_str)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON parameters: {e}"}, indent=2))
        sys.exit(1)

    result = DISPATCH[tool_name](params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
