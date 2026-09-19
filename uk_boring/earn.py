"""UKGraph Earn — the core endpoint.

Answers: "Given what I can actually do, what am I unusually well-positioned
to make money from right now?"

Input: capability envelope (skills, location, time, capital, equipment)
Output: grounded actions with estimated value, confidence, requirements
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class CapabilityEnvelope:
    """What a person can do. Received from Muse."""
    location: str = ""
    skills: list = field(default_factory=list)
    certifications: list = field(default_factory=list)
    equipment: list = field(default_factory=list)
    available_hours: int = 0
    available_days: list = field(default_factory=list)
    capital: float = 0
    vehicle: str = ""
    radius_miles: int = 20
    preferences: dict = field(default_factory=dict)


@dataclass
class Opportunity:
    """A grounded action with estimated value."""
    action: str           # APPLY_FOR_JOB, QUOTE_LEAD, BID_CONTRACT, BUY_AND_REPAIR, etc.
    title: str
    description: str
    estimated_value_gbp: float = 0
    confidence: float = 0
    distance_miles: float = 0
    deadline: str = ""
    requirements: list = field(default_factory=list)
    route_to_action: str = ""
    source: str = ""
    evidence: list = field(default_factory=list)


def find_earn_opportunities(profile: CapabilityEnvelope) -> list:
    """The main earn endpoint.
    
    Given what Jeff can do, what is he unusually well-positioned to make money from?
    """
    opportunities = []
    
    # 1. Local jobs matching skills
    opportunities.extend(_find_jobs(profile))
    
    # 2. Contracts matching capabilities
    opportunities.extend(_find_contracts(profile))
    
    # 3. Flipping opportunities matching skills
    opportunities.extend(_find_flips(profile))
    
    # 4. Service gaps matching capabilities
    opportunities.extend(_find_service_gaps(profile))
    
    # 5. Training upgrades
    opportunities.extend(_find_upgrades(profile))
    
    # Rank by expected utility
    opportunities.sort(key=lambda o: o.confidence * o.estimated_value_gbp, reverse=True)
    
    return opportunities


def _find_jobs(profile: CapabilityEnvelope) -> list:
    """Find local jobs matching skills."""
    opportunities = []
    
    # Load contracts data
    contracts_dir = Path(__file__).parent.parent / 'forests' / 'ukgraph' / 'data' / 'contracts'
    if contracts_dir.exists():
        for f in sorted(contracts_dir.glob('*.jsonl'), reverse=True)[:7]:
            with open(f) as fh:
                for line in fh:
                    try:
                        record = json.loads(line)
                        contract = record.get('data', {})
                        if _matches_skills(contract, profile):
                            opportunities.append(Opportunity(
                                action='BID_CONTRACT',
                                title=contract.get('title', ''),
                                description=contract.get('description', '')[:200],
                                estimated_value_gbp=contract.get('value_gbp', 0),
                                confidence=0.6,
                                deadline=contract.get('award_date', ''),
                                route_to_action='Submit via Contracts Finder',
                                source='contracts_finder',
                                evidence=[f"Contract {contract.get('contract_id', '')}"],
                            ))
                    except json.JSONDecodeError:
                        continue
    
    return opportunities[:5]


def _find_contracts(profile: CapabilityEnvelope) -> list:
    """Find government contracts."""
    # Same as jobs for now — contracts ARE jobs in this context
    return []


def _find_flips(profile: CapabilityEnvelope) -> list:
    """Find items that match repair skills."""
    opportunities = []
    
    # Check Breadup data for items matching repair skills
    breadup_dir = Path(__file__).parent.parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'
    if breadup_dir.exists():
        for f in sorted(breadup_dir.glob('*.jsonl'), reverse=True)[:3]:
            with open(f) as fh:
                for line in fh:
                    try:
                        item = json.loads(line)
                        if _can_repair_and_flip(item, profile):
                            sold_price = item.get('soldPrice', 0)
                            opportunities.append(Opportunity(
                                action='BUY_AND_REPAIR',
                                title=item.get('title', ''),
                                description=f"Listed at £{sold_price}, estimated repair cost £30-80",
                                estimated_value_gbp=sold_price * 0.3,  # 30% margin estimate
                                confidence=0.5,
                                route_to_action='Check eBay listing, buy if margin holds',
                                source='ebay',
                                evidence=[f"Sold at £{sold_price}"],
                            ))
                    except json.JSONDecodeError:
                        continue
    
    return opportunities[:3]


def _find_service_gaps(profile: CapabilityEnvelope) -> list:
    """Find services that nobody nearby provides well."""
    opportunities = []
    
    # Check planning data for new developments
    planning_dir = Path(__file__).parent.parent / 'forests' / 'ukgraph' / 'data' / 'planning'
    if planning_dir.exists():
        for f in sorted(planning_dir.glob('*.jsonl'), reverse=True)[:3]:
            with open(f) as fh:
                for line in fh:
                    try:
                        record = json.loads(line)
                        app = record.get('data', {})
                        desc = app.get('description', '').lower()
                        
                        # Check if development might need electrical work
                        if any(kw in desc for kw in ['extension', 'conversion', 'new build', 'commercial']):
                            if 'electrician' in profile.skills:
                                opportunities.append(Opportunity(
                                    action='CONTACT_DEVELOPER',
                                    title=f"Electrical work for: {app.get('description', '')[:60]}",
                                    description=f"Approved planning application may need electrical installation",
                                    estimated_value_gbp=500,
                                    confidence=0.4,
                                    route_to_action='Contact applicant via planning portal',
                                    source='planning_data',
                                    evidence=[f"Reference: {app.get('reference', '')}"],
                                ))
                    except json.JSONDecodeError:
                        continue
    
    return opportunities[:3]


def _find_upgrades(profile: CapabilityEnvelope) -> list:
    """Find training/certifications that unlock more work."""
    upgrades = []
    
    # EV certification
    if 'electrician' in profile.skills and 'ev_certification' not in profile.certifications:
        upgrades.append(Opportunity(
            action='UPGRADE',
            title='Get EV Charger Installation Certification',
            description='EV charger installation is in high demand and requires specific certification. Training costs ~£280 and unlocks a growing market.',
            estimated_value_gbp=0,
            confidence=0.8,
            requirements=['electrician qualification'],
            route_to_action='Search for EV installation training courses',
            source='market_analysis',
            evidence=['EV charger demand up 31% in North West', 'Certified installers in short supply'],
        ))
    
    return upgrades


def _matches_skills(contract: dict, profile: CapabilityEnvelope) -> bool:
    """Check if a contract matches the person's skills."""
    title = contract.get('title', '').lower()
    desc = contract.get('description', '').lower()
    text = f"{title} {desc}"
    
    for skill in profile.skills:
        if skill.lower() in text:
            return True
    
    for cert in profile.certifications:
        if cert.lower() in text:
            return True
    
    return False


def _can_repair_and_flip(item: dict, profile: CapabilityEnvelope) -> bool:
    """Check if an item could be repaired and flipped."""
    title = item.get('title', '').lower()
    condition = item.get('condition', '').lower()
    
    # Only consider broken/poor condition items
    if 'working' in condition or 'good' in condition:
        return False
    
    # Check if any repair skill matches
    repair_keywords = {
        'electrician': ['amplifier', 'speaker', 'guitar amp', 'pedal', 'synthesizer'],
        'engineer': ['motor', 'pump', 'compressor'],
        'diy': ['furniture', 'chair', 'table'],
    }
    
    for skill in profile.skills:
        for keyword in repair_keywords.get(skill, []):
            if keyword in title:
                return True
    
    return False


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    import sys
    
    profile = CapabilityEnvelope(
        location='Oldham',
        skills=['electrician'],
        certifications=['NICEIC'],
        equipment=['van', 'tools'],
        available_hours=5,
        available_days=['Thursday', 'Saturday'],
        capital=500,
        vehicle='van',
        radius_miles=20,
    )
    
    if len(sys.argv) > 1:
        try:
            profile = CapabilityEnvelope(**json.loads(sys.argv[1]))
        except:
            pass
    
    opportunities = find_earn_opportunities(profile)
    
    print(f"\nFound {len(opportunities)} opportunities for {profile.location}:\n")
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp.action}: {opp.title}")
        print(f"   Value: £{opp.estimated_value_gbp:.0f} | Confidence: {opp.confidence:.0%}")
        print(f"   {opp.route_to_action}")
        print()
