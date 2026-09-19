#!/usr/bin/env python3
"""
UKGraph MCP Server — UK Markets Intelligence (PR5 Truth Contract)

Tools:
- wage_growth:           ASHE Table 15 earnings by SOC × Region (the foundation)
- career_crowding:       Is a career getting crowded?
- trade_demand:          Demand-to-worker ratio for UK trades
- business_gap:          Find underserved business opportunities by postcode
- regulation_impact:     Analyze economic impact of UK regulations
- salary_data:           Get salary/wage data for an occupation
- local_job_trend:       What's happening to jobs in an area
- find_shortages:        What is Britain running out of
- find_skill_opportunities: What skills are scarce in an area
- market_gap:            Is there room for a business in a city
- wage_growth_map:       Where wages are rising fastest
- data_status:           Transparency tool — what data is actually available

Usage:
    python ukgraph_mcp.py                     # List tools
    python ukgraph_mcp.py <tool> '<json>'     # Call tool
    python ukgraph_mcp.py --serve             # MCP stdio server
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
import hashlib

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core import TruthClass, ActionClass, CapabilityResult

# ============================================================
# CONSTANTS
# ============================================================

DATAGOVUK_API = 'https://data.gov.uk/api'
LONDON_DATASTORE_API = 'https://data.london.gov.uk/api/3/action'
ONS_API = 'https://api.beta.ons.gov.uk/v1'
POSTCODES_IO_API = 'https://api.postcodes.io'

UK_REGIONS = [
    'london', 'south east', 'south west', 'east midlands', 'west midlands',
    'north west', 'north east', 'yorkshire and the humber', 'east of england',
    'scotland', 'wales', 'northern ireland',
]

REGION_SYNONYMS = {
    'london': 'london', 'south east': 'south east', 'south west': 'south west',
    'east midlands': 'east midlands', 'west midlands': 'west midlands',
    'north west': 'north west', 'north east': 'north east',
    'yorkshire and the humber': 'yorkshire and the humber',
    'yorkshire': 'yorkshire and the humber', 'east of england': 'east of england',
    'east anglia': 'east of england', 'scotland': 'scotland', 'wales': 'wales',
    'northern ireland': 'northern ireland', 'uk': 'united kingdom',
    'england': 'england', 'great britain': 'great britain',
}

ASHE_TABLE_15_URL = (
    'https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/'
    'earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15'
)

SOC4_LABELS = {
    '1111': 'Chief executives and senior officials',
    '1112': 'Functional managers and directors',
    '1121': 'Farmers',
    '1211': 'Production managers',
    '1212': 'Quality assurance managers',
    '1213': 'Transport and distribution managers',
    '1219': 'Managers and directors n.e.c.',
    '1221': 'Financial managers',
    '1222': 'Marketing and sales directors',
    '1223': 'Purchasing managers',
    '1224': 'Human resource managers',
    '1231': 'Construction managers',
    '1232': 'Environmental health officers',
    '1233': 'Care managers',
    '1234': 'Residential day care managers',
    '2111': 'Chemical scientists',
    '2112': 'Biological scientists',
    '2113': 'Biochemists and biomedical scientists',
    '2114': 'Physical scientists',
    '2115': 'Social scientists',
    '2121': 'Civil engineers',
    '2122': 'Mechanical engineers',
    '2123': 'Electrical engineers',
    '2124': 'Electronic engineers',
    '2126': 'Design and development engineers',
    '2127': 'Production and process engineers',
    '2129': 'Engineering professionals n.e.c.',
    '2131': 'IT and telecommunications directors',
    '2132': 'Software developers',
    '2133': 'Data analysts and programmers',
    '2134': 'Web design professionals',
    '2135': 'IT project managers',
    '2136': 'IT managers',
    '2139': 'Information technology professionals n.e.c.',
    '2211': 'Medical practitioners',
    '2212': 'Dentists',
    '2213': 'Optometrists',
    '2214': 'Pharmacists',
    '2215': 'Veterinarians',
    '2216': 'Medical radiographers',
    '2217': 'Podiatrists',
    '2219': 'Health professionals n.e.c.',
    '2221': 'Physiotherapists',
    '2222': 'Occupational therapists',
    '2223': 'Speech and language therapists',
    '2229': 'Therapy professionals n.e.c.',
    '2231': 'Midwives',
    '2232': 'Nurses',
    '2233': 'Nurse practitioners',
    '2234': 'Mental health nurses',
    '2235': 'District nurses',
    '2239': 'Nursing professionals n.e.c.',
    '2241': 'Dental practitioners',
    '2242': 'Dental nurses',
    '2249': 'Dental professionals n.e.c.',
    '2251': 'Veterinarians',
    '2252': 'Vet nurses',
    '2311': 'Higher education teaching professionals',
    '2312': 'Further education teaching professionals',
    '2314': 'Secondary education teaching professionals',
    '2315': 'Primary education teaching professionals',
    '2316': 'Special education needs teachers',
    '2317': 'Senior professionals of educational establishments',
    '2319': 'Teaching professionals n.e.c.',
    '2411': 'Barristers and judges',
    '2412': 'Solicitors',
    '2419': 'Legal professionals n.e.c.',
    '2421': 'Chartered and certified accountants',
    '2422': 'Financial controllers',
    '2423': 'Treasury managers',
    '2429': 'Finance professionals n.e.c.',
    '2431': 'Advertising and marketing directors',
    '2432': 'Market researchers',
    '2433': 'Marketing associate professionals',
    '2441': 'Architects',
    '2442': 'Landscape architects',
    '2443': 'Town planners',
    '2451': 'Social workers',
    '2452': 'Youth workers',
    '2461': 'Clergy',
    '2462': 'Reiki practitioners',
    '2491': 'Civil service officers',
    '2492': 'Political officers',
    '2493': 'Trade union officials',
    '2494': 'Charity workers',
    '2499': 'Miscellaneous professions n.e.c.',
    '3111': 'Nursing auxiliaries',
    '3112': 'Ambulance staff',
    '3113': 'Dental nurses',
    '3114': 'Houseparents',
    '3119': 'Healthcare assistants n.e.c.',
    '3121': 'Cleaners',
    '3211': 'Opticians',
    '3212': 'Pharmacy technicians',
    '3213': 'Dispensers',
    '3219': 'Science technicians n.e.c.',
    '3221': 'Yoga teachers',
    '3222': 'Fitness instructors',
    '3229': 'Sports coaches, instructors and officials n.e.c.',
    '3231': 'Hairdressers and barbers',
    '3232': 'Beauticians',
    '3233': 'Make-up artists',
    '3239': 'Business and domestic service occupations n.e.c.',
    '3411': 'Artists',
    '3412': 'Authors, writers and translators',
    '3413': 'Actors, entertainers and presenters',
    '3414': 'Dancers and choreographers',
    '3415': 'Musicians',
    '3416': 'Arts officers, producers and directors',
    '3417': 'Photographers',
    '3419': 'Arts and entertainment occupations n.e.c.',
    '3421': 'Interior designers',
    '3422': 'Product designers',
    '3423': 'Clothing designers',
    '3429': 'Design occupations n.e.c.',
    '3511': 'Agents and business managers',
    '3512': 'Auctioneers',
    '3513': 'Valuers and assessors',
    '3514': 'Inspectors',
    '3519': 'Business and related associate professionals n.e.c.',
    '3521': 'Banks and building societies',
    '3522': 'Insurance brokers',
    '3523': 'Fund managers',
    '3529': 'Financial and related associate professionals n.e.c.',
    '3531': 'Ship and boat officers',
    '3532': 'Pilots and flight engineers',
    '3533': 'Air traffic controllers',
    '3534': 'Clergy',
    '3539': 'Transport associate professionals n.e.c.',
    '3541': 'Legislators and senior officials',
    '3542': 'Judges',
    '3543': 'Senior officials of religious organisations',
    '3544': 'Senior local government officers',
    '3545': 'Senior officers of charity organisations',
    '3550': 'Senior positions n.e.c.',
    '4111': 'Farmers',
    '4112': 'Horticultural trades',
    '4121': 'Gardeners and groundskeepers',
    '4122': 'Grounds maintenance workers',
    '4131': 'Farm managers',
    '4132': 'Animal care and welfare services',
    '4133': 'Veterinary nurses',
    '4139': 'Animal care services n.e.c.',
    '4211': 'Shelf fillers',
    '4212': 'Retail cashiers and checkout operators',
    '4213': 'Demand-driven occupation',
    '4214': 'Pharmacy assistants',
    '4215': 'Undertakers and mortuary assistants',
    '4219': 'Sales occupations n.e.c.',
    '4221': 'Sales assistants and retail cashiers',
    '4222': 'Sales representatives',
    '4223': 'Sales accounts managers',
    '4224': 'Telesales persons',
    '4225': 'Market research interviewers',
    '4226': 'Street traders',
    '4227': 'Debt, rent and other collection officers',
    '4229': 'Sales and related occupations n.e.c.',
    '5111': 'Farm managers',
    '5112': 'Supervisors, forestry and related',
    '5113': 'Animal handlers and trainers',
    '5119': 'Agricultural and related trades n.e.c.',
    '5121': 'Bakers and flour confectioners',
    '5122': 'Butchers',
    '5123': 'Fishmongers and delicatessen',
    '5124': 'Poultry processors',
    '5125': 'Food preparation and catering trades n.e.c.',
    '5126': 'Cooks',
    '5211': 'Printers',
    '5212': 'Bookbinders',
    '5213': 'Lithographic and pre-press workers',
    '5214': 'Packers and labellers',
    '5219': 'Paper and wood machine operators n.e.c.',
    '5221': 'Waste disposal and recycling occupations',
    '5222': 'Street cleaners',
    '5223': 'Sewage plant operators',
    '5224': 'Refuse and salvage workers',
    '5231': 'Construction and building trades',
    '5232': 'Painters and decorators',
    '5233': 'Plasterers',
    '5234': 'Tilers',
    '5235': 'Scaffolders, steeplejacks and riggers',
    '5236': 'Floorers and wall tilers',
    '5237': 'Bricklayers',
    '5238': 'Builders',
    '5239': 'Other construction and building trades',
    '5241': 'Plumbers',
    '5242': 'Heating and ventilating engineers',
    '5243': 'Air conditioning engineers',
    '5244': 'Gas engineers',
    '5245': 'Electricians',
    '5246': 'Cable jointers and jointers',
    '5249': 'Electrical installation occupations n.e.c.',
    '5250': 'Skilled metal and electrical occupations',
    '5251': 'Ironers, pressers and waders',
    '5252': 'Tailors and dressmakers',
    '5253': 'Upholsterers',
    '5254': 'Leather cutters and sewers',
    '5255': 'Drapers and warehousepersons',
    '5256': 'Shoe repairers and hatters',
    '5259': 'Textile, garment and related occupations n.e.c.',
    '5261': 'Jewellery and precision instrument makers',
    '5262': 'Musical instrument makers',
    '5263': 'Tool makers, pattern makers and model makers',
    '5264': 'Cabinet makers',
    '5265': 'Glaziers',
    '5266': 'Stone masons and related trades',
    '5267': 'Signwriters',
    '5268': 'Sports equipment makers',
    '5269': 'Handicraft and related occupations n.e.c.',
    '5311': 'Coach and vehicle body builders',
    '5312': 'Motor mechanics',
    '5313': 'Auto electricians',
    '5314': 'Vehicle body repairers',
    '5315': 'Vehicle paint sprayers',
    '5319': 'Mobile plant maintenance occupations n.e.c.',
    '5321': 'Aircraft maintenance and related trades',
    '5322': 'Marine maintenance and related trades',
    '5323': 'Rail and rolling stock maintenance and related trades',
    '5329': 'Plant maintenance occupations n.e.c.',
    '5411': 'Steel erectors',
    '5412': 'Scaffolders',
    '5413': 'Riggers',
    '5414': 'Floorers and carpet fitters',
    '5415': 'Removal men',
    '5419': 'Mobile machine drivers and operatives n.e.c.',
    '5421': 'Mobile machine drivers and operatives',
    '5422': 'Construction plant operators',
    '5423': 'Crane drivers',
    '5424': 'Road construction operatives',
    '5425': 'Rail construction and maintenance operatives',
    '5426': 'Transport operatives',
    '5429': 'Operative construction occupations n.e.c.',
    '5511': 'Packers, bottlers, canners and weighers',
    '5512': 'Food, drink and tobacco process operatives',
    '5513': 'Textile process operatives',
    '5514': 'Garment making and related occupations',
    '5519': 'Process operatives n.e.c.',
    '5521': 'Pulp and paper making operatives',
    '5522': 'Printing machine operators',
    '5523': 'Paper product machine operatives',
    '5529': 'Paper and wood machine operatives n.e.c.',
    '6111': 'Agricultural and horticultural operatives',
    '6112': 'Gardeners and groundskeepers',
    '6113': 'Tree surgeons',
    '6114': 'Animal handlers',
    '6119': 'Agricultural and related occupations n.e.c.',
    '6121': 'Forestry workers',
    '6122': 'Fishery workers',
    '6129': 'Fishing and related occupations n.e.c.',
    '6131': 'Coal miners',
    '6132': 'Quarry workers',
    '6133': 'Oil and gas workers',
    '6139': 'Mining and related occupations n.e.c.',
    '6211': 'Meat process operatives',
    '6212': 'Bakers',
    '6213': 'Food process operatives',
    '6214': 'Tobacco process operatives',
    '6219': 'Food preparation and related operatives n.e.c.',
    '6221': 'Glass and ceramics process operatives',
    '6222': 'Chemical and related process operatives',
    '6223': 'Rubber process operatives',
    '6224': 'Plastics process operatives',
    '6229': 'Chemical, glass, ceramics and related process operatives n.e.c.',
    '6231': 'Metal casting and finishing operatives',
    '6232': 'Welders',
    '6233': 'Solderers and braziers',
    '6234': 'Metal working machine operators',
    '6235': 'Metal polishers',
    '6239': 'Metal process operatives n.e.c.',
    '6241': 'Machine tool operators',
    '6242': 'Fitters and mechanics',
    '6243': 'CNC machine tool programmers',
    '6244': 'Tool and die makers',
    '6249': 'Engineering and related operatives n.e.c.',
    '6251': 'Electrical and electronic equipment assembly',
    '6252': 'Electrical assembly and related trades',
    '6253': 'Electronic assembly and related trades',
    '6259': 'Electrical and electronic assembly occupations n.e.c.',
    '6261': 'Inspectors and other manufacturing occupations',
    '6262': 'Weavers and textile operatives',
    '6263': 'Knitters and hosiery operatives',
    '6264': 'Embroiderers and textile traders',
    '6265': 'Upholsterers and textile traders',
    '6269': 'Textile and garment occupations n.e.c.',
    '6291': 'Furniture makers and other woodworkers',
    '6292': 'Woodworking machine operators',
    '6299': 'Woodworking and related occupations n.e.c.',
    '7111': 'Warehouse managers',
    '7112': 'Shelf fillers',
    '7113': 'Stock control clerks',
    '7121': 'Packers and labellers',
    '7122': 'Weighers and graders',
    '7123': 'Clerical and warehouse occupations n.e.c.',
    '7124': 'Team leaders',
    '7125': 'Sorters',
    '7129': 'Warehouse occupations n.e.c.',
    '7211': 'Construction occupations',
    '7212': 'Construction plant operators',
    '7213': 'Scaffolders and riggers',
    '7214': 'Bricklayers and masons',
    '7215': 'Painters and decorators',
    '7216': 'Plasterers and related trades',
    '7217': 'Floorers and wall tilers',
    '7218': 'Glaziers',
    '7219': 'Construction trades n.e.c.',
    '7221': 'Plumbers',
    '7222': 'Heating and ventilating installers',
    '7223': 'Air conditioning installers',
    '7224': 'Gas engineers',
    '7225': 'Electricians',
    '7226': 'Cable jointers',
    '7229': 'Electrical installation occupations n.e.c.',
    '7231': 'Ironers, pressers and waders',
    '7232': 'Tailors and dressmakers',
    '7233': 'Upholsterers',
    '7234': 'Leather cutters and sewers',
    '7235': 'Drapers and warehousepersons',
    '7236': 'Shoe repairers and hatters',
    '7239': 'Textile, garment and related occupations n.e.c.',
    '7241': 'Jewellery and precision instrument makers',
    '7242': 'Musical instrument makers',
    '7243': 'Tool makers, pattern makers and model makers',
    '7244': 'Cabinet makers',
    '7245': 'Glaziers',
    '7246': 'Stone masons and related trades',
    '7247': 'Signwriters',
    '7248': 'Sports equipment makers',
    '7249': 'Handicraft and related occupations n.e.c.',
    '7251': 'Coach and vehicle body builders',
    '7252': 'Motor mechanics',
    '7253': 'Auto electricians',
    '7254': 'Vehicle body repairers',
    '7255': 'Vehicle paint sprayers',
    '7259': 'Mobile plant maintenance occupations n.e.c.',
    '7261': 'Aircraft maintenance and related trades',
    '7262': 'Marine maintenance and related trades',
    '7263': 'Rail and rolling stock maintenance and related trades',
    '7269': 'Plant maintenance occupations n.e.c.',
    '7311': 'Steel erectors',
    '7312': 'Scaffolders',
    '7313': 'Riggers',
    '7314': 'Floorers and carpet fitters',
    '7315': 'Removal men',
    '7319': 'Mobile machine drivers and operatives n.e.c.',
    '7321': 'Mobile machine drivers and operatives',
    '7322': 'Construction plant operators',
    '7323': 'Crane drivers',
    '7324': 'Road construction operatives',
    '7325': 'Rail construction and maintenance operatives',
    '7326': 'Transport operatives',
    '7329': 'Operative construction occupations n.e.c.',
    '7411': 'Packers, bottlers, canners and weighers',
    '7412': 'Food, drink and tobacco process operatives',
    '7413': 'Textile process operatives',
    '7414': 'Garment making and related occupations',
    '7419': 'Process operatives n.e.c.',
    '7421': 'Pulp and paper making operatives',
    '7422': 'Printing machine operators',
    '7423': 'Paper product machine operatives',
    '7429': 'Paper and wood machine operatives n.e.c.',
    '8111': 'Production line operatives',
    '8112': 'Quality control and related occupations',
    '8113': 'Assembly and related occupations',
    '8114': 'HGV drivers',
    '8115': 'Van drivers',
    '8116': 'Bus and coach drivers',
    '8117': 'Delivery drivers',
    '8118': 'Drivers of industrial trucks and cranes',
    '8119': 'Mobile machine drivers and operatives n.e.c.',
    '8121': 'Process operatives',
    '8122': 'Construction operatives',
    '8123': 'Food preparation and related occupations',
    '8124': 'Glass and ceramics process operatives',
    '8125': 'Chemical and related process operatives',
    '8126': 'Rubber process operatives',
    '8127': 'Plastics process operatives',
    '8129': 'Chemical, glass, ceramics and related process operatives n.e.c.',
    '8131': 'Metal casting and finishing operatives',
    '8132': 'Welders',
    '8133': 'Solderers and braziers',
    '8134': 'Metal working machine operators',
    '8135': 'Metal polishers',
    '8139': 'Metal process operatives n.e.c.',
    '8141': 'Machine tool operators',
    '8142': 'Fitters and mechanics',
    '8143': 'CNC machine tool programmers',
    '8144': 'Tool and die makers',
    '8149': 'Engineering and related operatives n.e.c.',
    '8151': 'Electrical and electronic equipment assembly',
    '8152': 'Electrical assembly and related trades',
    '8153': 'Electronic assembly and related trades',
    '8159': 'Electrical and electronic assembly occupations n.e.c.',
    '8161': 'Inspectors and other manufacturing occupations',
    '8162': 'Weavers and textile operatives',
    '8163': 'Knitters and hosiery operatives',
    '8164': 'Embroiderers and textile traders',
    '8165': 'Upholsterers and textile traders',
    '8169': 'Textile and garment occupations n.e.c.',
    '8171': 'Furniture makers and other woodworkers',
    '8172': 'Woodworking machine operators',
    '8179': 'Woodworking and related occupations n.e.c.',
    '8211': 'Assemblers',
    '8212': 'Packers and labellers',
    '8213': 'Weighers and graders',
    '8214': 'Warehouse occupations',
    '8215': 'Team leaders',
    '8219': 'Elementary occupations n.e.c.',
    '8221': 'Construction occupations',
    '8222': 'Construction plant operators',
    '8223': 'Scaffolders and riggers',
    '8224': 'Bricklayers and masons',
    '8225': 'Painters and decorators',
    '8226': 'Plasterers and related trades',
    '8227': 'Floorers and wall tilers',
    '8228': 'Glaziers',
    '8229': 'Construction trades n.e.c.',
    '8231': 'Ironers, pressers and waders',
    '8232': 'Tailors and dressmakers',
    '8233': 'Upholsterers',
    '8234': 'Leather cutters and sewers',
    '8235': 'Drapers and warehousepersons',
    '8236': 'Shoe repairers and hatters',
    '8239': 'Textile, garment and related occupations n.e.c.',
    '8241': 'Jewellery and precision instrument makers',
    '8242': 'Musical instrument makers',
    '8243': 'Tool makers, pattern makers and model makers',
    '8244': 'Cabinet makers',
    '8245': 'Glaziers',
    '8246': 'Stone masons and related trades',
    '8247': 'Signwriters',
    '8248': 'Sports equipment makers',
    '8249': 'Handicraft and related occupations n.e.c.',
    '8251': 'Coach and vehicle body builders',
    '8252': 'Motor mechanics',
    '8253': 'Auto electricians',
    '8254': 'Vehicle body repairers',
    '8255': 'Vehicle paint sprayers',
    '8259': 'Mobile plant maintenance occupations n.e.c.',
    '8261': 'Aircraft maintenance and related trades',
    '8262': 'Marine maintenance and related trades',
    '8263': 'Rail and rolling stock maintenance and related trades',
    '8269': 'Plant maintenance occupations n.e.c.',
    '8311': 'Steel erectors',
    '8312': 'Scaffolders',
    '8313': 'Riggers',
    '8314': 'Floorers and carpet fitters',
    '8315': 'Removal men',
    '8319': 'Mobile machine drivers and operatives n.e.c.',
    '8321': 'Mobile machine drivers and operatives',
    '8322': 'Construction plant operators',
    '8323': 'Crane drivers',
    '8324': 'Road construction operatives',
    '8325': 'Rail construction and maintenance operatives',
    '8326': 'Transport operatives',
    '8329': 'Operative construction occupations n.e.c.',
    '9111': 'Domestic housekeepers',
    '9112': 'Launderers, dry cleaners and pressers',
    '9113': 'Caretakers and school keepers',
    '9114': 'Cleaning and related occupations',
    '9119': 'Domestic occupations n.e.c.',
    '9121': 'Shelf fillers',
    '9122': 'Retail cashiers and checkout operators',
    '9123': 'Demand-driven occupation',
    '9124': 'Pharmacy assistants',
    '9125': 'Undertakers and mortuary assistants',
    '9129': 'Sales occupations n.e.c.',
    '9131': 'Shopkeepers and retail managers',
    '9132': 'Market traders and stallholders',
    '9133': 'Debt, rent and other collection officers',
    '9139': 'Sales and related occupations n.e.c.',
    '9211': 'Agricultural and horticultural operatives',
    '9212': 'Gardeners and groundskeepers',
    '9213': 'Tree surgeons',
    '9214': 'Animal handlers',
    '9219': 'Agricultural and related occupations n.e.c.',
    '9221': 'Forestry workers',
    '9222': 'Fishery workers',
    '9229': 'Fishing and related occupations n.e.c.',
    '9231': 'Coal miners',
    '9232': 'Quarry workers',
    '9233': 'Oil and gas workers',
    '9239': 'Mining and related occupations n.e.c.',
    '9241': 'Meat process operatives',
    '9242': 'Bakers',
    '9243': 'Food process operatives',
    '9244': 'Tobacco process operatives',
    '9249': 'Food preparation and related operatives n.e.c.',
    '9251': 'Glass and ceramics process operatives',
    '9252': 'Chemical and related process operatives',
    '9253': 'Rubber process operatives',
    '9254': 'Plastics process operatives',
    '9259': 'Chemical, glass, ceramics and related process operatives n.e.c.',
    '9261': 'Metal casting and finishing operatives',
    '9262': 'Welders',
    '9263': 'Solderers and braziers',
    '9264': 'Metal working machine operators',
    '9265': 'Metal polishers',
    '9269': 'Metal process operatives n.e.c.',
    '9271': 'Machine tool operators',
    '9272': 'Fitters and mechanics',
    '9273': 'CNC machine tool programmers',
    '9274': 'Tool and die makers',
    '9279': 'Engineering and related operatives n.e.c.',
    '9281': 'Electrical and electronic equipment assembly',
    '9282': 'Electrical assembly and related trades',
    '9283': 'Electronic assembly and related trades',
    '9289': 'Electrical and electronic assembly occupations n.e.c.',
    '9291': 'Inspectors and other manufacturing occupations',
    '9292': 'Weavers and textile operatives',
    '9293': 'Knitters and hosiery operatives',
    '9294': 'Embroiderers and textile traders',
    '9295': 'Upholsterers and textile traders',
    '9299': 'Textile and garment occupations n.e.c.',
}

# ============================================================
# PR5 RESPONSE CONTRACT
# ============================================================

def _response(
    capability: str,
    result: dict,
    truth_class: TruthClass = TruthClass.CONCEPTUAL,
    confidence: float = 0.0,
    evidence: list = None,
    method_id: str = '',
    method_version: str = '1.0',
    action_class: ActionClass = ActionClass.ADVISORY,
    limitations: list = None,
) -> dict:
    """Build a PR5-compliant response envelope."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        'capability': capability,
        'as_of': now,
        'result': result,
        'truth_class': truth_class.value,
        'confidence': confidence,
        'evidence': evidence or [],
        'method': {'id': method_id, 'version': method_version},
        'limitations': limitations or [],
        'action': {'class': action_class.value},
    }


# ============================================================
# DATA STATUS
# ============================================================

def data_status():
    """Transparency tool — what data is actually available right now."""
    return _response(
        capability='ukgraph.data_status',
        result={
            'data_sources': [
                {
                    'id': 'ashe_table15',
                    'name': 'ASHE Table 15 — Region by Occupation (4-digit SOC)',
                    'url': ASHE_TABLE_15_URL,
                    'status': 'PARTIAL',
                    'freshness': '2021',
                    'record_count': 100,
                    'truth_class': TruthClass.VERIFIED.value,
                    'what_it_covers': 'Median annual pay by SOC 4-digit × Region × Year',
                    'how_to_collect': 'Download XLS from ONS, parse Table 15 tabs, normalise SOC codes',
                },
                {
                    'id': 'ashe_table14',
                    'name': 'ASHE Table 14 — Occupation by Region',
                    'url': 'https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupationbyregion4digitsoc2010ashetable14',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Gross weekly pay, annual pay, hours by SOC × Region',
                },
                {
                    'id': 'claimant_count',
                    'name': 'ONS Claimant Count by local authority',
                    'url': 'https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/claimantcountbylocalauthority',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Number of claimants by age and duration, by LA',
                },
                {
                    'id': 'vacancies',
                    'name': 'ONS Vacancies by industry and region',
                    'url': 'https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/vacanciesbyindustry',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Vacancies by industry sector, time series',
                },
                {
                    'id': 'business_demography',
                    'name': 'ONS UK Business: Activity, Size and Location',
                    'url': 'https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/datasets/ukbusinessactivitysizeandlocation',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Business births, deaths, active stock by SIC × LA',
                },
                {
                    'id': 'companies_house',
                    'name': 'Companies House API — company register',
                    'url': 'https://api.company-information.service.gov.uk/',
                    'status': 'NOT_INTEGRATED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Company registrations, appointments, filings by postcode',
                },
                {
                    'id': 'neet',
                    'name': 'ONS NEET statistics by age',
                    'url': 'https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/peopleaged16to24neet',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'NEET rates by age, gender, region',
                },
                {
                    'id': 'hesa_graduates',
                    'name': 'HESA graduate outcomes by subject',
                    'url': 'https://www.hesa.ac.uk/data-and-analysis/graduates',
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Graduate counts by subject, institution, employment outcomes',
                },
                {
                    'id': 'job_advert_index',
                    'name': 'CEBR/Adzuna job advert index',
                    'url': None,
                    'status': 'NOT_COLLECTED',
                    'freshness': None,
                    'record_count': 0,
                    'what_it_covers': 'Real-time job advert volume by sector and region',
                },
            ],
            'collection_status': 'No data has been collected yet. All tools are returning conceptual or unavailable responses. This is correct behaviour under the PR5 truth contract.',
            'next_steps': [
                'Collect ASHE Table 15 XLS files (2014–present) and parse SOC × Region earnings',
                'Integrate ONS Claimant Count API for demand-side signals',
                'Connect Companies House API for business formation/death data',
                'Collect HESA graduate output for supply-side signals',
            ],
        },
        truth_class=TruthClass.CONCEPTUAL,
        confidence=1.0,
        method_id='ukgraph.data_status',
        limitations=[
            'All underlying datasets report NOT_COLLECTED. This tool exists for transparency.',
        ],
    )


# ============================================================
# WAGE GROWTH (the foundation tool)
# ============================================================

def wage_growth(soc_code=None, occupation=None, region=None, start_year=None, end_year=None):
    """ASHE Table 15: earnings by SOC 4-digit x Region, year-on-year change.

    Returns real data from canonical store if available.
    """
    resolved_soc = soc_code
    if not resolved_soc and occupation:
        resolved_soc = _resolve_occupation_to_soc(occupation)
    if not resolved_soc:
        resolved_soc = 'unknown'

    resolved_region = _normalise_region(region)
    now_year = datetime.now(timezone.utc).year
    actual_start = start_year or (now_year - 2)
    actual_end = end_year or (now_year - 1)

    ashe_data = _get_ashe_data(resolved_soc, resolved_region)
    
    if ashe_data:
        pay_by_year = {}
        for record in ashe_data:
            year = record.get('year')
            pay = record.get('median_annual_pay')
            if year and pay:
                pay_by_year[year] = pay
        
        if pay_by_year:
            latest_year = max(pay_by_year.keys())
            latest_pay = pay_by_year[latest_year]
            
            result = {
                'soc_code': resolved_soc,
                'soc_label': ashe_data[0].get('occupation_name', occupation or 'Unknown'),
                'region': resolved_region or 'All UK regions',
                'period': str(latest_year),
                'data_source': 'ASHE Table 15 (via canonical store)',
                'url': ASHE_TABLE_15_URL,
                'median_annual_pay': latest_pay,
                'available_years': sorted(pay_by_year.keys()),
                'sample_size': len(ashe_data),
            }
            
            return _response(
                capability='ukgraph.wage_growth',
                result=result,
                truth_class=TruthClass.VERIFIED,
                confidence=0.9,
                evidence=[f'ASHE data: {len(ashe_data)} records for SOC {resolved_soc}'],
                method_id='ukgraph.wage_growth.ashe_canonical',
                limitations=[],
            )
    
    result = {
        'soc_code': resolved_soc,
        'soc_label': SOC4_LABELS.get(resolved_soc, occupation or 'Unknown'),
        'region': resolved_region or 'All UK regions',
        'period': f'{actual_start}-{actual_end}',
        'data_source': 'ASHE Table 15',
        'url': ASHE_TABLE_15_URL,
        'method_description': (
            'ASHE Table 15, SOC 4-digit x Region, median annual pay, '
            'year-on-year change.'
        ),
    }

    return _response(
        capability='ukgraph.wage_growth',
        result=result,
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.wage_growth.ashe_table15',
        limitations=[
            'No ASHE data found for this SOC code/region combination.',
        ],
    )


def _get_ashe_data(soc_code=None, region=None):
    """Load ASHE data from canonical store."""
    try:
        from core.normalize import load_observations
        observations = load_observations('ukgraph', source='ashe_earnings', limit=1000)
        
        results = []
        for obs in observations:
            value = obs.get('value', {})
            if soc_code and value.get('occupation_code') != soc_code:
                continue
            if region and region.lower() not in value.get('region', '').lower():
                continue
            results.append(value)
        
        return results
    except Exception:
        return []


def _resolve_occupation_to_soc(occupation):
    """Best-effort text match to SOC 4-digit code."""
    if not occupation:
        return None
    occ_lower = occupation.lower().strip()

    direct_map = {
        'nurse': '2232', 'registered nurse': '2232', 'nursing': '2232',
        'doctor': '2211', 'medical practitioner': '2211', 'physician': '2211',
        'dentist': '2212', 'dental': '2212',
        'pharmacist': '2214', 'pharmacy': '2214',
        'vet': '2215', 'veterinarian': '2215', 'veterinary': '2215',
        'optometrist': '2213', 'optician': '3211',
        'therapist': '2229', 'physiotherapist': '2221',
        'midwife': '2231', 'midwives': '2231',
        'electrician': '5241', 'electric': '5241', 'electrical engineer': '2123', 'electrical': '2123',
        'plumber': '5241', 'plumbing': '5241',
        'gas engineer': '5244', 'gas': '5244',
        'carpenter': '5264', 'joiner': '5264', 'carpentry': '5264',
        'bricklayer': '5237', 'bricklaying': '5237',
        'plasterer': '5233', 'plastering': '5233',
        'roofer': '5239', 'roofing': '5239',
        'painter': '5232', 'decorator': '5232', 'painting and decorating': '5232',
        'tiler': '5234', 'tiling': '5234',
        'glazier': '5265', 'glazing': '5265',
        'welder': '5232', 'welding': '5232',
        'mechanic': '5312', 'motor mechanic': '5312', 'motor vehicle mechanic': '5312',
        'chef': '5611', 'cook': '5611', 'cooking': '5611',
        'software developer': '2132', 'software': '2132', 'developer': '2132',
        'data analyst': '2133', 'data scientist': '2133', 'programmer': '2133',
        'cyber security': '2136', 'cyber': '2136', 'cloud': '2136', 'devops': '2136',
        'teacher': '2314', 'teaching': '2314', 'lecturer': '2312',
        'architect': '2441', 'architectural': '2441',
        'accountant': '2421', 'accounting': '2421',
        'lawyer': '2412', 'solicitor': '2412', 'legal': '2412',
        'care worker': '6145', 'care': '6145', 'domiciliary care': '6145',
        'paramedic': '3212',
        'graphic designer': '3422', 'designer': '3422',
        'marketing': '2433', 'sales': '4221',
        'consultant': '2423', 'management consultant': '2423',
        'project manager': '2135', 'product manager': '2135',
        'hr': '2242', 'human resources': '2242',
        'barber': '3231', 'hairdresser': '3231', 'hairdressing': '3231',
        'pilot': '3532', 'airline pilot': '3532',
        'driver': '8211', 'hgv driver': '8211', 'delivery driver': '8211',
        'cleaner': '9111', 'cleaning': '9111',
        'security': '8143', 'security guard': '8143',
    }

    for key, code in direct_map.items():
        if key in occ_lower:
            return code

    for code, label in SOC4_LABELS.items():
        if occ_lower in label.lower():
            return code

    return None


# ============================================================
# CAREER CROWDING
# ============================================================

def career_crowding(occupation, region=None):
    """Is a career getting crowded?

    Requires: ASHE wage growth + ONS Claimant Count (demand) + HESA (graduate supply).
    Formula: constraint_tightness = demand_growth / (entrant_growth + existing_supply)
    """
    resolved_soc = _resolve_occupation_to_soc(occupation)
    resolved_region = _normalise_region(region)

    formula = {
        'constraint_tightness': (
            'demand_growth / (entrant_growth + existing_supply)'
        ),
        'components': {
            'demand_growth': {
                'source': 'ONS Vacancies by industry + ONS Claimant Count',
                'required_data': [
                    'Vacancy counts by SOC or industry sector (monthly)',
                    'Claimant count by occupation group (monthly)',
                    'Ratio trend over 2+ years',
                ],
                'currently_available': False,
            },
            'entrant_growth': {
                'source': 'HESA graduate output by subject + Skills England/Ifate starts',
                'required_data': [
                    'Graduate numbers by subject, last 3 years',
                    'Apprenticeship starts by level and sector',
                    'Career changer data (inferred from NEET and retraining)',
                ],
                'currently_available': False,
            },
            'existing_supply': {
                'source': 'BRES employment by occupation + ASHE hours data',
                'required_data': [
                    'Employed persons by SOC 4-digit (annual)',
                    'Average hours worked (ASHE Table 14)',
                    'Inactivity and retirement flows',
                ],
                'currently_available': False,
            },
        },
        'interpretation': (
            'constraint_tightness > 1.0 → market is tight, wages should rise. '
            'constraint_tightness < 1.0 → oversupply, career is crowded. '
            'Combine with wage_growth() direction to confirm.'
        ),
        'occupational_profile': {
            'soc_code': resolved_soc,
            'soc_label': SOC4_LABELS.get(resolved_soc, occupation),
            'region': resolved_region or 'National',
        },
    }

    return _response(
        capability='ukgraph.career_crowding',
        result={
            'occupation': occupation,
            'region': resolved_region or 'National',
            'soc_code': resolved_soc,
            'formula': formula,
            'verdict': 'UNAVAILABLE — data sources not yet integrated',
            'advice': (
                'This tool requires three data sources that are not yet collected. '
                'See data_status() for collection plan.'
            ),
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.career_crowding.constraint_tightness',
        limitations=[
            'Requires ASHE Table 15 for wage growth signal',
            'Requires ONS Claimant Count for demand-side proxy',
            'Requires HESA graduate data for supply-side signal',
            'Without these, any crowding score would be fabricated',
        ],
    )


# ============================================================
# TRADE DEMAND
# ============================================================

def trade_demand(trade, region=None):
    """Demand-to-worker ratio for UK trades.

    Requires: ONS Vacancies (demand) + ASHE/BRES (supply).
    """
    resolved_region = _normalise_region(region)

    return _response(
        capability='ukgraph.trade_demand',
        result={
            'trade': trade,
            'region': resolved_region or 'National',
            'demand_to_worker_ratio': None,
            'data_requirements': {
                'demand_signal': {
                    'source': 'ONS Vacancies by industry (time series)',
                    'proxy': 'Reed/Cv-Library job adverts if ONS granularity insufficient',
                    'currently_available': False,
                },
                'supply_signal': {
                    'source': 'BRES employment by SOC + ASHE hours worked',
                    'alternative': 'Census occupation data (2021)',
                    'currently_available': False,
                },
                'method': (
                    'demand_to_worker_ratio = demand_growth_rate / supply_growth_rate. '
                    'Ratio > 1.5 = shortage, < 0.8 = oversupply.'
                ),
            },
            'known_limitations': (
                'ONS Vacancies by detailed trade is not published at SOC level. '
                'Use industry-level proxies (construction, health, etc.) and cross-reference '
                'with Migration Advisory Committee shortage occupation list.'
            ),
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.trade_demand.demand_worker_ratio',
        limitations=[
            'ONS does not publish vacancies at 4-digit SOC level',
            'Supply data (BRES by SOC) is annual and lags by ~6 months',
            'Real-time proxy needed: job board scraping or Adzuna index',
        ],
    )


# ============================================================
# BUSINESS GAP
# ============================================================

def business_gap(postcode, sector):
    """Find undersered business opportunities by postcode.

    Uses: postcodes.io (resolve to LA) + Companies House (business data).
    """
    postcode_upper = postcode.upper().strip()
    district = postcode_upper.split()[0] if postcode_upper else postcode_upper

    local_authority = _resolve_postcode_to_la(postcode_upper)

    return _response(
        capability='ukgraph.business_gap',
        result={
            'postcode': postcode_upper,
            'district': district,
            'local_authority': local_authority,
            'sector': sector,
            'data_requirements': {
                'business_counts': {
                    'source': 'Companies House API or ONS UK Business: Activity, Size and Location',
                    'method': (
                        'Query Companies House by registered postcode + SIC code. '
                        'Count active companies in SIC group for the sector. '
                        'Compare against population/workforce for per-capita ratio.'
                    ),
                    'currently_available': False,
                },
                'population_density': {
                    'source': 'ONS Mid-year Population Estimates',
                    'method': 'Population aged 16-74 in local authority as denominator',
                    'currently_available': False,
                },
                'business_formation_rate': {
                    'source': 'ONS Business Demography UK (births and deaths)',
                    'method': (
                        'Business birth rate minus death rate = net formation. '
                        'If formation rate is high but per-capita count is low → gap.'
                    ),
                    'currently_available': False,
                },
                'retail_footfall': {
                    'source': 'Springboard footfall data (commercial)',
                    'alternative': 'ONS Retail Sales Index by region',
                    'currently_available': False,
                },
            },
            'formula': (
                'opportunity_score = (area_business_density < national_median) '
                'AND (birth_rate > national_average) AND (per_capita_income > threshold)'
            ),
            'resolution_method': (
                f'1. Call postcodes.io/{postcode_upper} → get admin_district\n'
                f'2. Match admin_district to ONS LA code\n'
                f'3. Query Companies House or ONS business data by LA + SIC\n'
                f'4. Compute per-capita density vs national benchmark'
            ),
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.business_gap.postcode_sector',
        limitations=[
            'Requires Companies House API integration (free, key optional)',
            'SIC codes to sector mapping is coarse — need a lookup table',
            'Population denominator is LA-level, not postcode-level',
        ],
    )


def _resolve_postcode_to_la(postcode):
    """Resolve a UK postcode to local authority via postcodes.io."""
    import urllib.request
    import urllib.error
    import urllib.parse

    try:
        url = f'{POSTCODES_IO_API}/postcodes/{urllib.parse.quote(postcode)}'
        req = urllib.request.Request(url, headers={'User-Agent': 'datagarden-ukgraph/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            if data.get('status') == 200:
                result = data.get('result', {})
                return {
                    'admin_district': result.get('admin_district'),
                    'admin_district_code': result.get('codes', {}).get('admin_district'),
                    'region': result.get('region'),
                    'parliamentary_constituency': result.get('parliamentary_constituency'),
                }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        pass
    return None


# ============================================================
# REGULATION IMPACT
# ============================================================

def regulation_impact(query):
    """Analyse economic impact of UK regulations.

    Requires: ASHE earnings + ONS business demography + policy impact assessments.
    """
    return _response(
        capability='ukgraph.regulation_impact',
        result={
            'query': query,
            'analysis_framework': {
                'affected_sectors': {
                    'method': 'Cross-reference regulation scope with SIC codes',
                    'data_source': 'Regulatory impact assessment (gov.uk) + ONS SIC mapping',
                    'currently_available': False,
                },
                'worker_impact': {
                    'method': 'ASHE earnings pre/post implementation, by affected SOC codes',
                    'data_source': 'ASHE Table 15 + ASHE Table 14',
                    'currently_available': False,
                },
                'business_impact': {
                    'method': 'Business formation/death rates in affected sectors vs control',
                    'data_source': 'ONS Business Demography UK',
                    'currently_available': False,
                },
                'regional_impact': {
                    'method': 'Regional concentration of affected industries',
                    'data_source': 'BRES employment by industry × region',
                    'currently_available': False,
                },
            },
            'regulatory_sources': [
                'https://www.legislation.gov.uk/ — primary legislation',
                'https://www.gov.uk/government/publications — policy papers and impact assessments',
                'https://hansard.parliament.uk/ — parliamentary debate records',
            ],
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.regulation_impact.sectoral',
        limitations=[
            'Regulation impact is inherently causal and hard to isolate',
            'Requires access to regulatory impact assessments which vary in quality',
            'ASHE data lags by ~6 months, making real-time impact assessment impossible',
        ],
    )


# ============================================================
# SALARY DATA
# ============================================================

def salary_data(occupation, region=None):
    """Get salary/wage data for an occupation.

    Uses ASHE data from canonical store if available.
    """
    resolved_soc = _resolve_occupation_to_soc(occupation)
    resolved_region = _normalise_region(region)

    ashe_data = _get_ashe_data(resolved_soc, resolved_region)
    
    if ashe_data:
        record = ashe_data[0]
        median_pay = record.get('median_annual_pay')
        mean_pay = record.get('mean_annual_pay')
        hourly_pay = round(median_pay / 2080, 2) if median_pay else None
        
        result = {
            'occupation': record.get('occupation_name', occupation),
            'region': record.get('region', resolved_region or 'National'),
            'soc_code': resolved_soc,
            'median_annual_pay': median_pay,
            'mean_annual_pay': mean_pay,
            'median_hourly_pay': hourly_pay,
            'year': record.get('year'),
            'sample_size': record.get('num_jobs_thousands'),
        }
        
        return _response(
            capability='ukgraph.salary_data',
            result=result,
            truth_class=TruthClass.VERIFIED,
            confidence=0.9,
            evidence=[f'ASHE data: {len(ashe_data)} records for SOC {resolved_soc}'],
            method_id='ukgraph.salary_data.ashe_canonical',
            limitations=[],
        )
    
    return _response(
        capability='ukgraph.salary_data',
        result={
            'occupation': occupation,
            'region': resolved_region or 'National',
            'soc_code': resolved_soc,
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.salary_data.ashe_tables',
        limitations=[
            'No ASHE data found for this occupation/region combination.',
        ],
    )


# ============================================================
# LOCAL JOB TREND
# ============================================================

def local_job_trend(postcode):
    """What's happening to jobs in an area.

    Requires: ONS Business Demography + Claimant Count by local authority.
    """
    postcode_upper = postcode.upper().strip()
    local_authority = _resolve_postcode_to_la(postcode_upper)

    return _response(
        capability='ukgraph.local_job_trend',
        result={
            'postcode': postcode_upper,
            'local_authority': local_authority,
            'data_requirements': {
                'employment_trend': {
                    'source': 'ONS BRES employment by local authority',
                    'method': 'Year-on-year change in employee jobs by LA',
                    'currently_available': False,
                },
                'claimant_trend': {
                    'source': 'ONS Claimant Count by local authority',
                    'method': 'Monthly claimant count, seasonally adjusted, 12-month change',
                    'currently_available': False,
                },
                'business_formation': {
                    'source': 'ONS Business Demography by local authority',
                    'method': 'Business births and deaths in LA, rolling 12 months',
                    'currently_available': False,
                },
                'sector_mix': {
                    'source': 'ONS Business Register by SIC × LA',
                    'method': 'Sector composition of the local economy vs national',
                    'currently_available': False,
                },
            },
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.local_job_trend.local_authority',
        limitations=[
            'Postcode to local authority resolution requires postcodes.io (free, no key)',
            'ONS local authority data is published quarterly, not real-time',
            'Granularity below LA level is not available from official sources',
        ],
    )


# ============================================================
# FIND SHORTAGES
# ============================================================

def find_shortages(region=None):
    """What is Britain running out of.

    Synthesis tool — joins multiple data sources.
    Requires: (1) ASHE wage growth, (2) Claimant Count trends,
              (3) ONS job advert indices, (4) Business formation/death rates
    """
    resolved_region = _normalise_region(region)

    return _response(
        capability='ukgraph.find_shortages',
        result={
            'region': resolved_region or 'National',
            'synthesis_framework': {
                'step_1_wage_signal': {
                    'description': 'Occupations with accelerating wage growth signal shortage',
                    'source': 'ASHE Table 15 — year-on-year median pay growth by SOC × Region',
                    'threshold': 'Wage growth > CPIH + 2% for 2+ consecutive years',
                    'currently_available': False,
                },
                'step_2_demand_signal': {
                    'description': 'Occupations with rising claimant-to-vacancy ratio signal demand',
                    'source': 'ONS Claimant Count + Vacancies by industry',
                    'threshold': 'Vacancy growth > 10% YoY while claimant count stable/falling',
                    'currently_available': False,
                },
                'step_3_supply_signal': {
                    'description': 'Occupations with shrinking graduate/apprentice output',
                    'source': 'HESA graduate counts + Ifate/Skills England starts',
                    'threshold': 'Entry-level pipeline declining or flat while demand rises',
                    'currently_available': False,
                },
                'step_4_business_signal': {
                    'description': 'Sectors with high business death rates relative to births',
                    'source': 'ONS Business Demography UK',
                    'threshold': 'Net business death rate > 5% for 2+ years',
                    'currently_available': False,
                },
                'synthesis_method': (
                    'Combine all four signals. Shortage = positive wage signal '
                    'AND positive demand signal AND negative supply signal. '
                    'Weight by recency and confidence of each data source.'
                ),
            },
            'known_shortage_list': {
                'source': 'Migration Advisory Committee Shortage Occupation List',
                'url': 'https://www.gov.uk/government/publications/shortage-occupation-list',
                'note': 'This is a policy list, not a data-derived list. Use as validation.',
            },
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.find_shortages.multi_source_synthesis',
        limitations=[
            'This is the most complex tool — requires 4+ data sources integrated',
            'Each source has different release cadence (monthly/quarterly/annual)',
            'Shortage is relative to region, not absolute',
            'The MAC shortage list is politically determined, not purely economic',
        ],
    )


# ============================================================
# FIND SKILL OPPORTUNITIES
# ============================================================

def find_skill_opportunities(postcode, budget=None):
    """What could I learn that's scarce.

    Requires: ASHE wage growth + Vacancy data + Graduate supply data.
    """
    postcode_upper = postcode.upper().strip()
    local_authority = _resolve_postcode_to_la(postcode_upper)

    return _response(
        capability='ukgraph.find_skill_opportunities',
        result={
            'postcode': postcode_upper,
            'local_authority': local_authority,
            'budget': f'£{budget}' if budget else 'No limit',
            'analysis_method': {
                'demand_ranking': {
                    'source': 'ONS Vacancies by industry + Adzuna/Reed job board data',
                    'method': 'Rank sectors by vacancy growth rate, weighted by regional concentration',
                    'currently_available': False,
                },
                'supply_inverse': {
                    'source': 'HESA graduates by subject + Ifate apprenticeship starts',
                    'method': 'Inverse of graduate output = how few people are entering this field',
                    'currently_available': False,
                },
                'earnings_premium': {
                    'source': 'ASHE Table 14 — hourly pay by SOC',
                    'method': 'Earnings premium = (sector median - national median) / national median',
                    'currently_available': False,
                },
                'breakeven_calculation': {
                    'method': 'Training cost / (monthly earnings premium × full-time equivalent)',
                    'inputs': ['Course cost estimate', 'ASHE earnings data', 'Time to employment'],
                    'currently_available': False,
                },
            },
            'training_providers': {
                'note': 'Links to national training databases — not yet integrated',
                'sources': [
                    'https://www.find-training.service.gov.uk/ — government course finder',
                    'https://www.citb.co.uk/ — construction training',
                    'https://www.cityandguilds.com/ — vocational qualifications',
                ],
            },
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.find_skill_opportunities.demand_supply',
        limitations=[
            'Cannot rank skills without vacancy and graduate data',
            'Training costs are estimates, not verified',
            'Regional skill demand varies — postcode resolution helps but LA data is coarse',
        ],
    )


# ============================================================
# MARKET GAP
# ============================================================

def market_gap(business_type, city):
    """Is there room for a business in a city.

    Requires: ONS Business Demography + Population density + Sector SIC mapping.
    """
    return _response(
        capability='ukgraph.market_gap',
        result={
            'business_type': business_type,
            'city': city.title(),
            'analysis_framework': {
                'existing_supply': {
                    'method': 'Count active companies in SIC group for the city/area',
                    'source': 'Companies House API or ONS Business: Activity, Size and Location',
                    'currently_available': False,
                },
                'population_demand': {
                    'method': 'Per-capita business density vs national benchmark',
                    'source': 'ONS Mid-year Population Estimates + Business stock',
                    'currently_available': False,
                },
                'formation_rate': {
                    'method': 'Recent business births and deaths in the sector and area',
                    'source': 'ONS Business Demography UK',
                    'currently_available': False,
                },
                'spending_power': {
                    'method': 'ONS ASHE earnings in the area as proxy for disposable income',
                    'source': 'ASHE Table 15 by region',
                    'currently_available': False,
                },
            },
            'sector_to_sic_mapping': {
                'note': 'A SIC code lookup table is needed to map business_type to Standard Industrial Classification',
                'reference': 'https://www.ons.gov.uk/methodology/classificationsandstandards/standardindustrialclassificationofeconomicactivities',
                'currently_available': False,
            },
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.market_gap.city_sector',
        limitations=[
            'Business type to SIC code mapping is essential and not yet built',
            'City-level data requires Companies House API (postcode-based queries)',
            'Spending power is estimated, not directly observed at postcode level',
        ],
    )


# ============================================================
# WAGE GROWTH MAP
# ============================================================

def wage_growth_map(region=None, occupation=None):
    """Where wages are rising fastest for an occupation.

    Should use ASHE Table 15 across regions.
    """
    resolved_soc = _resolve_occupation_to_soc(occupation)
    resolved_region = _normalise_region(region)

    return _response(
        capability='ukgraph.wage_growth_map',
        result={
            'occupation': occupation or 'All occupations',
            'region': resolved_region or 'All UK regions',
            'soc_code': resolved_soc,
            'method': {
                'description': (
                    'ASHE Table 15: for each region, extract median annual pay '
                    'for the SOC 4-digit code, compute year-on-year growth, '
                    'rank regions by growth rate.'
                ),
                'data_source': ASHE_TABLE_15_URL,
                'currently_available': False,
            },
            'expected_output': {
                'per_region': [
                    {
                        'region': '<region>',
                        'median_annual_pay': None,
                        'yoy_change_pct': None,
                        'yoy_change_real_pct': None,
                        'rank': None,
                    }
                ],
                'fastest_growing': None,
                'slowest_growing': None,
            },
        },
        truth_class=TruthClass.UNAVAILABLE,
        confidence=0.0,
        evidence=[],
        method_id='ukgraph.wage_growth_map.ashe_table15',
        limitations=[
            'ASHE Table 15 data not yet collected',
            'Some SOC codes have small samples at regional level — suppress for reliability',
            'Year-on-year changes are more volatile for smaller occupations/regions',
        ],
    )


# ============================================================
# HELPERS
# ============================================================

def _normalise_region(region):
    """Normalise a region string to canonical form."""
    if not region:
        return None
    region_lower = region.lower().strip()
    return REGION_SYNONYMS.get(region_lower, region.title())


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = [
    {
        "name": "data_status",
        "description": "Transparency tool — shows what UKGraph data is actually available right now. Lists each data source, its freshness, and record count. Use this first to understand what the other tools can and cannot do.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "wage_growth",
        "description": "ASHE Table 15: earnings by SOC 4-digit x Region, year-on-year change. The foundation tool for all UKGraph labour market analysis. Returns UNAVAILABLE until ASHE data is collected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "soc_code": {"type": "string", "description": "SOC 4-digit code (e.g. '2232' for nurse)"},
                "occupation": {"type": "string", "description": "Job role — will be resolved to SOC code (e.g. 'nurse', 'electrician')"},
                "region": {"type": "string", "description": "UK region (e.g. 'London', 'North West')"},
                "start_year": {"type": "integer", "description": "Start year for comparison (default: 2 years ago)"},
                "end_year": {"type": "integer", "description": "End year for comparison (default: last year)"}
            }
        }
    },
    {
        "name": "career_crowding",
        "description": "Is a career getting crowded? Requires ASHE wage growth + ONS Claimant Count (demand) + HESA (graduate supply). Formula: constraint_tightness = demand_growth / (entrant_growth + existing_supply). Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'electrician', 'software developer')"},
                "region": {"type": "string", "description": "UK region (e.g. 'London', 'North West', 'Scotland')"}
            },
            "required": ["occupation"]
        }
    },
    {
        "name": "trade_demand",
        "description": "Demand-to-worker ratio for UK trades. Requires ONS Vacancies (demand) + ASHE/BRES (supply). Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trade": {"type": "string", "description": "Trade name (e.g. 'electrician', 'plumber', 'bricklayer')"},
                "region": {"type": "string", "description": "UK region (e.g. 'London', 'West Midlands')"}
            },
            "required": ["trade"]
        }
    },
    {
        "name": "business_gap",
        "description": "Find undersered business opportunities by postcode. Uses postcodes.io to resolve to local authority, then queries Companies House or ONS business data. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode (e.g. 'SW1A 1AA', 'M1 1AE')"},
                "sector": {"type": "string", "description": "Business sector (e.g. 'cafe', 'gym', 'pharmacy', 'childcare')"}
            },
            "required": ["postcode", "sector"]
        }
    },
    {
        "name": "regulation_impact",
        "description": "Analyse economic impact of UK regulations. Requires ASHE earnings + ONS business demography + policy impact assessments. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Regulation or policy query (e.g. 'minimum wage increase', 'IR35', 'Brexit trade barriers')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "salary_data",
        "description": "Get salary/wage data for an occupation. Should use ASHE Table 14/15. Returns UNAVAILABLE until ASHE data is collected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'software developer', 'bricklayer')"},
                "region": {"type": "string", "description": "UK region (default: national average)"}
            },
            "required": ["occupation"]
        }
    },
    {
        "name": "local_job_trend",
        "description": "What's happening to jobs in an area. Requires ONS Business Demography + Claimant Count by local authority. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode or district (e.g. 'E1', 'SW1A', 'M1')"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "find_shortages",
        "description": "What is Britain running out of. Synthesis tool joining (1) ASHE wage growth, (2) Claimant Count trends, (3) ONS job advert indices, (4) Business formation/death rates. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "UK region (default: national)"}
            }
        }
    },
    {
        "name": "find_skill_opportunities",
        "description": "What could I learn that's scarce. Requires ASHE wage growth + Vacancy data + Graduate supply data. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode or district for local context"},
                "budget": {"type": "number", "description": "Max training budget in GBP (default: no limit)"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "market_gap",
        "description": "Is there room for a business in a city. Requires ONS Business Demography + Population density + Sector SIC mapping. Returns UNAVAILABLE until data is integrated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "business_type": {"type": "string", "description": "Type of business (e.g. 'bubble tea shop', 'dog grooming', 'coworking space')"},
                "city": {"type": "string", "description": "UK city (e.g. 'Manchester', 'Birmingham', 'Leeds')"}
            },
            "required": ["business_type", "city"]
        }
    },
    {
        "name": "wage_growth_map",
        "description": "Where wages are rising fastest for an occupation. Uses ASHE Table 15 across regions. Returns UNAVAILABLE until ASHE data is collected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "UK region to focus on"},
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'developer')"}
            }
        }
    },
]


# ============================================================
# DISPATCH
# ============================================================

DISPATCH = {t['name']: globals()[t['name']] for t in TOOLS}


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
                    "serverInfo": {
                        "name": "ukgraph",
                        "version": "2.0.0",
                        "description": (
                            "UKGraph — UK markets intelligence. PR5 truth contract. "
                            "All tools return honest truth_class ratings. "
                            "Use data_status() to see what data is available."
                        ),
                    },
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
        print(json.dumps({"name": "ukgraph", "version": "2.0.0", "tools": [t["name"] for t in TOOLS]}, indent=2))
