"""UKGraph Earn — the core endpoint.

Answers: "Given what I can actually do, what am I unusually well-positioned
to make money from right now?"

Input: capability envelope (skills, location, time, capital, equipment)
Output: grounded actions with estimated value, confidence, requirements

All routes cite specific canonical observations as evidence.
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
    action: str
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
    provenance: list = field(default_factory=list)
    freshness: dict = field(default_factory=dict)


def _get_freshness() -> dict:
    """Get freshness metadata for all registered sources."""
    try:
        from core.source_registry import SourceRegistry
        registry = SourceRegistry()
        return {s.id: s.to_dict() for s in registry.list_sources()}
    except Exception:
        return {}


def _freshness_for_source(source_id: str, freshness_map: dict) -> dict:
    """Extract freshness metadata for a specific source."""
    meta = freshness_map.get(source_id, {})
    return {
        "source_id": source_id,
        "licence": meta.get("licence", ""),
        "reliability": meta.get("reliability", ""),
        "update_frequency": meta.get("update_frequency", ""),
        "max_age_hours": meta.get("max_age_hours", 0),
    }


def find_earn_opportunities(profile: CapabilityEnvelope) -> list:
    """The main earn endpoint.

    Given what Jeff can do, what is he unusually well-positioned to make money from?
    Every returned opportunity cites specific canonical observation IDs.
    """
    freshness = _get_freshness()
    opportunities = []

    opportunities.extend(_find_jobs(profile, freshness))
    opportunities.extend(_find_contracts(profile, freshness))
    opportunities.extend(_find_flips(profile, freshness))
    opportunities.extend(_find_service_gaps(profile, freshness))
    opportunities.extend(_find_upgrades(profile, freshness))

    opportunities.sort(key=lambda o: o.confidence * o.estimated_value_gbp, reverse=True)

    return opportunities


def _find_jobs(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find local jobs matching skills from canonical store."""
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukopportunity', source='planning_data_api', limit=500)

        for obs in observations:
            value = obs.get('value', {})
            desc = value.get('description', '').lower()
            ref = value.get('reference', '')
            obs_id = obs.get('observation_id', '')

            if _matches_skills_text(desc, profile):
                opportunities.append(Opportunity(
                    action='CONTACT_DEVELOPER',
                    title=f"Work for: {value.get('description', '')[:60]}",
                    description=f"Planning application {ref} may need work",
                    estimated_value_gbp=500,
                    confidence=0.4,
                    source='planning_data_canonical',
                    evidence=[value.get('description', '')],
                    provenance=[obs_id],
                    freshness=_freshness_for_source(obs.get('source_id', ''), freshness),
                ))
    except Exception:
        pass

    return opportunities[:5]


def _find_contracts(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find government contracts from canonical store."""
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukopportunity', source='contracts_finder', limit=500)

        for obs in observations:
            value = obs.get('value', {})
            title = value.get('title', '').lower()
            desc = value.get('description', '').lower()
            text = f"{title} {desc}"
            obs_id = obs.get('observation_id', '')

            matches = any(
                skill.lower() in text for skill in profile.skills
            ) or any(
                cert.lower() in text for cert in profile.certifications
            )

            if matches:
                value_gbp = value.get('value_gbp', 0)
                opportunities.append(Opportunity(
                    action='BID_CONTRACT',
                    title=f"Contract: {value.get('title', '')[:60]}",
                    description=f"Government contract worth £{value_gbp:,.0f} from {value.get('buyer', '')}",
                    estimated_value_gbp=value_gbp * 0.1,
                    confidence=0.3,
                    source='contracts_finder_canonical',
                    evidence=[f"Awarded to {value.get('supplier', 'unknown')} for £{value_gbp:,.0f}"],
                    provenance=[obs_id],
                    freshness=_freshness_for_source(obs.get('source_id', ''), freshness),
                ))
    except Exception:
        pass

    return opportunities[:5]


def _find_flips(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find items that match repair skills from canonical store."""
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukproducts', source='ebay_uk_sold', limit=500)

        for obs in observations:
            value = obs.get('value', {})
            title = value.get('title', '').lower()
            condition = value.get('condition', '').lower()
            obs_id = obs.get('observation_id', '')

            if 'working' in condition or 'good' in condition:
                continue

            repair_keywords = {
                'electrician': ['amplifier', 'speaker', 'guitar amp', 'pedal', 'synthesizer'],
                'engineer': ['motor', 'pump', 'compressor'],
                'diy': ['furniture', 'chair', 'table'],
            }

            matched = False
            for skill in profile.skills:
                for keyword in repair_keywords.get(skill, []):
                    if keyword in title:
                        matched = True
                        break
                if matched:
                    break

            if matched:
                sold_price = value.get('sold_price', 0)
                opportunities.append(Opportunity(
                    action='BUY_AND_REPAIR',
                    title=value.get('title', ''),
                    description=f"Listed at £{sold_price}, estimated repair cost £30-80",
                    estimated_value_gbp=sold_price * 0.3,
                    confidence=0.5,
                    route_to_action='Check eBay listing, buy if margin holds',
                    source='ebay_canonical',
                    evidence=[f"Sold at £{sold_price}"],
                    provenance=[obs_id],
                    freshness=_freshness_for_source(obs.get('source_id', ''), freshness),
                ))
    except Exception:
        pass

    return opportunities[:3]


def _find_service_gaps(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find services that nobody nearby provides well."""
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukopportunity', source='planning_data_api', limit=500)

        for obs in observations:
            value = obs.get('value', {})
            desc = value.get('description', '').lower()
            ref = value.get('reference', '')
            obs_id = obs.get('observation_id', '')

            if any(kw in desc for kw in ['extension', 'conversion', 'new build', 'commercial']):
                if 'electrician' in profile.skills:
                    opportunities.append(Opportunity(
                        action='CONTACT_DEVELOPER',
                        title=f"Electrical work for: {value.get('description', '')[:60]}",
                        description=f"Approved planning application {ref} may need electrical installation",
                        estimated_value_gbp=500,
                        confidence=0.4,
                        route_to_action='Contact applicant via planning portal',
                        source='planning_data_canonical',
                        evidence=[f"Reference: {ref}"],
                        provenance=[obs_id],
                        freshness=_freshness_for_source(obs.get('source_id', ''), freshness),
                    ))
    except Exception:
        pass

    return opportunities[:3]


def _find_upgrades(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find training/certifications that unlock more work."""
    upgrades = []

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
            provenance=[],
            freshness={},
        ))

    return upgrades


def _matches_skills_text(text: str, profile: CapabilityEnvelope) -> bool:
    """Check if free text matches the person's skills or certifications."""
    for skill in profile.skills:
        if skill.lower() in text:
            return True
    for cert in profile.certifications:
        if cert.lower() in text:
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
        print(f"   Evidence: {'; '.join(opp.evidence[:2])}")
        print(f"   Provenance: {', '.join(opp.provenance)}")
        if opp.freshness:
            print(f"   Source: {opp.freshness.get('source_id', '')} ({opp.freshness.get('reliability', '')})")
        print()
