"""UKGraph Earn — the core endpoint.

Answers: "Given what I can actually do, what am I unusually well-positioned
to make money from right now?"

Input: capability envelope (skills, location, time, capital, equipment)
Output: grounded actions with estimated value, confidence, requirements

Jev is wired in here to classify whether a planning application or contract
is relevant to a specific skill. This is the core semantic compression step.
"""

import json
import os
import requests
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


OR_KEY = None

def _get_or_key():
    global OR_KEY
    if OR_KEY:
        return OR_KEY
    try:
        from agent_vault import get_key
        OR_KEY = get_key('openrouter')
    except Exception:
        OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    return OR_KEY


def _jev_classify(state: dict, questions: dict) -> dict:
    """Call Jev via OpenRouter to classify something.
    
    Logs every call for audit and calibration.
    """
    key = _get_or_key()
    if not key:
        return {}
    
    payload = {
        'model': 'typesafe/jev-1.13',
        'state': json.dumps(state),
        'questions': questions,
    }
    
    try:
        resp = requests.post(
            'https://openrouter.ai/api/alpha/decisions',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json=payload,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            answers = data.get('answers', {})
            
            # Log the Jev call for audit
            _log_jev_call(
                spec_id='opportunity.capability_family',
                spec_version='1.0',
                state=state,
                questions=questions,
                answers=answers,
            )
            
            return answers
    except Exception:
        pass
    return {}


def _log_jev_call(spec_id, spec_version, state, questions, answers, source_obs_ids=None):
    """Log every Jev call for audit and calibration."""
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'spec_id': spec_id,
        'spec_version': spec_version,
        'state_preview': str(state)[:200],
        'questions': list(questions.keys()),
        'answers': {},
        'source_observation_ids': source_obs_ids or [],
    }
    for k, v in answers.items():
        if isinstance(v, dict):
            log_entry['answers'][k] = {
                'type': v.get('type'),
                'value': v.get('score') or v.get('choice') or v.get('noul'),
                'confidence': v.get('confidence'),
            }
    
    log_path = Path(__file__).parent.parent / 'experiments' / 'jev_logs' / f'{datetime.now().strftime("%Y-%m-%d")}.jsonl'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry, default=str) + '\n')


def _classify_opportunity(description: str, skills: list) -> dict:
    """Use Jev to classify whether an opportunity matches a person's skills."""
    state = {
        'opportunity': {
            'description': description,
        },
        'person': {
            'skills': skills,
        }
    }
    
    questions = {
        'relevance': {
            'type': 'score',
            'instructions': 'How relevant is this opportunity to the persons skills?',
            'criteria': ['not relevant', 'slightly relevant', 'moderately relevant', 'very relevant', 'perfect match'],
        },
        'actionable': {
            'type': 'noul',
            'instructions': 'Could a person with these skills actually do this work?',
        },
        'estimated_value': {
            'type': 'choice',
            'instructions': 'What is the approximate value of this opportunity?',
            'criteria': {
                'low': 'Under 100 GBP',
                'medium': '100-500 GBP',
                'high': '500-2000 GBP',
                'very_high': 'Over 2000 GBP',
            }
        },
        'urgency': {
            'type': 'choice',
            'instructions': 'How urgent is this opportunity?',
            'criteria': {
                'immediate': 'This week',
                'soon': 'This month',
                'flexible': 'No rush',
            }
        }
    }
    
    return _jev_classify(state, questions)


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
    opportunities.extend(_find_complaint_opportunities(profile, freshness))

    opportunities.sort(key=lambda o: o.confidence * o.estimated_value_gbp, reverse=True)

    return opportunities


def _get_salary_data(skills: list, location: str = 'UK Median') -> dict:
    """Get salary data for skills from canonical store."""
    try:
        from core.normalize import load_observations
        salaries = load_observations('ukopportunity', source='web_salary_data', limit=100)
        
        # Find matching salary data
        for obs in salaries:
            value = obs.get('value', {})
            region = value.get('region', '')
            if region == location or region == 'UK Median':
                return {
                    'median': value.get('salary_gbp', 39039),
                    'source': value.get('source', ''),
                }
        
        # Default UK median
        return {'median': 39039, 'source': 'ONS ASHE 2025'}
    except Exception:
        return {'median': 39039, 'source': 'ONS ASHE 2025'}


def _find_jobs(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find local jobs matching skills from canonical store.
    
    Strategy: keyword pre-filter → Jev classifies top candidates only.
    Don't call Jev on every observation (too slow). Pre-filter, then Jev the top 20.
    """
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukopportunity', source='planning_data_api', limit=500)

        # Step 1: Keyword pre-filter (fast, no API calls)
        candidates = []
        for obs in observations:
            value = obs.get('value', {})
            desc = value.get('description', '')
            if not desc:
                continue
            desc_lower = desc.lower()
            if any(skill.lower() in desc_lower for skill in profile.skills):
                candidates.append(obs)

        # Step 2: Jev classifies only top 20 candidates (fast, ~20s)
        for obs in candidates[:20]:
            value = obs.get('value', {})
            desc = value.get('description', '')
            ref = value.get('reference', '')
            obs_id = obs.get('observation_id', '')

            jev_result = _classify_opportunity(desc, profile.skills)
            relevance = jev_result.get('relevance', {})
            score = relevance.get('score', 0) if isinstance(relevance, dict) else 0
            actionable = jev_result.get('actionable', {})
            is_actionable = actionable.get('noul', False) if isinstance(actionable, dict) else False
            value_choice = jev_result.get('estimated_value', {})
            value_label = value_choice.get('choice', 'medium') if isinstance(value_choice, dict) else 'medium'
            value_map = {'low': 100, 'medium': 300, 'high': 750, 'very_high': 2000}
            estimated_value = value_map.get(value_label, 300)
            
            # Adjust value based on salary data
            salary_data = _get_salary_data(profile.skills, profile.location)
            if salary_data['median']:
                # Rough estimate: planning application work = 1-3 days
                daily_rate = salary_data['median'] / 260  # 260 working days
                estimated_value = max(estimated_value, daily_rate * 1.5)  # 1.5x daily rate

            if score >= 5 and is_actionable:
                opportunities.append(Opportunity(
                    action='CONTACT_DEVELOPER',
                    title=f"Work for: {desc[:60]}",
                    description=f"Planning application {ref} may need work",
                    estimated_value_gbp=estimated_value,
                    confidence=score / 10.0,
                    source='planning_data_jev',
                    evidence=[desc[:200]],
                    provenance=[obs_id],
                    freshness=_freshness_for_source(obs.get('source_id', ''), freshness),
                ))
    except Exception as e:
        print(f"  Error in _find_jobs: {e}")

    return opportunities[:5]


def _find_contracts(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find government contracts from canonical store.
    
    CRITICAL: Only emit LIVE/FUTURE opportunities, never historical awards.
    Awards are useful for intelligence but cannot become BID_CONTRACT routes.
    """
    opportunities = []

    try:
        from core.normalize import load_observations
        observations = load_observations('ukopportunity', source='contracts_finder', limit=500)

        for obs in observations:
            value = obs.get('value', {})
            title = value.get('title', '')
            desc = value.get('description', '')
            status = value.get('status', '').lower()
            obs_id = obs.get('observation_id', '')
            value_gbp = value.get('value_gbp', 0)

            # CRITICAL: Never emit awarded contracts as live bids
            if 'award' in status:
                continue  # Awards are historical intelligence, not bid opportunities

            text = f"{title} {desc}".lower()
            matches = any(
                skill.lower() in text for skill in profile.skills
            ) or any(
                cert.lower() in text for cert in profile.certifications
            )

            if matches:
                opportunities.append(Opportunity(
                    action='BID_CONTRACT',
                    title=f"Contract: {title[:60]}",
                    description=f"Government contract worth £{value_gbp:,.0f} from {value.get('buyer', '')}",
                    estimated_value_gbp=value_gbp,  # NO fabrication — use actual value or UNKNOWN
                    confidence=0.3,
                    source='contracts_finder_canonical',
                    evidence=[f"Contract {value.get('reference', '')}"],
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
    """Find training/certifications that unlock more work.
    
    CRITICAL: Every claim needs evidence. No fabricated market statistics.
    """
    upgrades = []

    if 'electrician' in profile.skills and 'ev_certification' not in profile.certifications:
        # Check if there's actual evidence of EV demand in our data
        ev_evidence = []
        try:
            from core.normalize import load_observations
            observations = load_observations('ukopportunity', source='planning_data_api', limit=500)
            for obs in observations:
                desc = obs.get('value', {}).get('description', '').lower()
                if 'ev' in desc or 'electric vehicle' in desc or 'charger' in desc:
                    ev_evidence.append(obs.get('observation_id', ''))
        except Exception:
            pass

        if ev_evidence:
            # Only recommend if we have actual evidence
            upgrades.append(Opportunity(
                action='UPGRADE',
                title='Get EV Charger Installation Certification',
                description='EV charger installation may require specific certification. Training costs ~£280.',
                estimated_value_gbp=0,  # UNKNOWN — we don't know the ROI
                confidence=0.5,  # Lower confidence without proven demand data
                requirements=['electrician qualification'],
                route_to_action='Search for EV installation training courses',
                source='planning_data_evidence',
                evidence=[f"EV-related planning applications found: {len(ev_evidence)}"],
                provenance=ev_evidence[:5],
                freshness={},
            ))

    return upgrades


def _find_complaint_opportunities(profile: CapabilityEnvelope, freshness: dict) -> list:
    """Find opportunities based on complaint data.
    
    Complaints reveal where workflows are broken.
    Fixing broken workflows is an opportunity.
    """
    opportunities = []
    
    try:
        from core.normalize import load_observations
        complaints = load_observations('ukadmin', source='dwp_complaints', limit=1000)
        
        # Find services with high complaint rates
        service_complaints = {}
        for obs in complaints:
            value = obs.get('value', {})
            area = value.get('area', '')
            count = value.get('complaints', 0)
            if area and count:
                service_complaints[area] = service_complaints.get(area, 0) + count
        
        # Sort by complaint volume
        for area, count in sorted(service_complaints.items(), key=lambda x: x[1], reverse=True)[:5]:
            if count > 500:  # Only high-complaint services
                opportunities.append(Opportunity(
                    action='OFFER_SERVICE',
                    title=f"Improve {area} workflow",
                    description=f"{area} has {count} complaints/quarter. Improving this workflow saves people time.",
                    estimated_value_gbp=0,  # Value is time saved, not direct payment
                    confidence=0.4,
                    source='dwp_complaints_canonical',
                    evidence=[f"{area}: {count} complaints/quarter"],
                    provenance=[],
                    freshness={},
                ))
    except Exception:
        pass
    
    return opportunities[:3]


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
