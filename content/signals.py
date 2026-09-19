"""
UKGraph Signal Detection — finds interesting changes in the graph.

Signals are detected from canonical observations.
A signal is eligible for content if:
- large change
- large geographic disparity
- unexpected divergence
- clear ranking
- clear winner/loser
- clear money implication
- clear action somebody can take
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from core.signal import Signal, ContentFrame


def detect_signals_from_planning(observations: list) -> List[Signal]:
    """Detect signals from planning application observations."""
    signals = []
    
    # Count applications by description keywords
    keyword_counts = {}
    for obs in observations:
        desc = obs.get('value', {}).get('description', '').lower()
        for keyword in ['extension', 'conversion', 'new build', 'solar', 'ev', 'commercial']:
            if keyword in desc:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Create signals for notable concentrations
    for keyword, count in keyword_counts.items():
        if count >= 3:  # threshold for signal
            signals.append(Signal(
                signal_id=f"plan_{keyword}_{datetime.now().strftime('%Y%m%d')}",
                entity=keyword,
                place="UK",
                metric="planning_concentration",
                change=count,
                window="snapshot",
                confidence=0.8,
                evidence=[obs.get('observation_id', '') for obs in observations[:5]],
                source_garden="ukopportunity",
                detected_at=datetime.now(timezone.utc).isoformat(),
            ))
    
    return signals


def detect_signals_from_contracts(observations: list) -> List[Signal]:
    """Detect signals from contract observations."""
    signals = []
    
    # Group by buyer
    buyers = {}
    for obs in observations:
        buyer = obs.get('value', {}).get('buyer', '')
        value = obs.get('value', {}).get('value_gbp', 0)
        if buyer and value > 0:
            if buyer not in buyers:
                buyers[buyer] = []
            buyers[buyer].append(value)
    
    # Create signals for active buyers
    for buyer, values in buyers.items():
        if len(values) >= 2:
            avg_value = sum(values) / len(values)
            signals.append(Signal(
                signal_id=f"contract_{buyer[:20]}_{datetime.now().strftime('%Y%m%d')}",
                entity=buyer,
                place="UK",
                metric="contract_activity",
                change=len(values),
                window="snapshot",
                confidence=0.7,
                evidence=[],
                source_garden="ukopportunity",
                detected_at=datetime.now(timezone.utc).isoformat(),
                related={"avg_value_gbp": avg_value, "total_contracts": len(values)},
            ))
    
    return signals


def score_signal(signal: Signal) -> float:
    """Score a signal's interestingness for content.
    
    interestingness = magnitude × confidence × novelty × human_relevance × actionability
    """
    # Magnitude: how big is the change?
    magnitude = min(abs(signal.change) / 10.0, 1.0)  # normalize to 0-1
    
    # Confidence: how sure are we?
    confidence = signal.confidence
    
    # Novelty: is this new? (hard to determine without history, use 0.5 default)
    novelty = 0.5
    
    # Human relevance: does this affect people?
    human_relevance = 0.7  # default, can be overridden
    
    # Actionability: can someone do something?
    actionability = 0.6  # default
    
    score = magnitude * confidence * novelty * human_relevance * actionability
    return round(score, 3)


def generate_content_frames(signal: Signal) -> list:
    """Generate content frames for a signal."""
    frames = []
    
    # Large change → CHANGE frame
    if abs(signal.change) > 0.15:
        frames.append("CHANGE")
    
    # Money implication → OPPORTUNITY frame
    if any(kw in signal.metric.lower() for kw in ['pay', 'salary', 'wage', 'earnings', 'revenue', 'profit', 'contract']):
        frames.append("OPPORTUNITY")
    
    # Geographic variation → WHERE frame
    if signal.place != "UK":
        frames.append("WHERE")
    
    # Comparison possible → COMPARE frame
    if signal.related:
        frames.append("COMPARE")
    
    # Warning indicators
    if signal.change < -0.2:
        frames.append("WARNING")
    
    # Default to OPPORTUNITY if no other frame
    if not frames:
        frames.append("OPPORTUNITY")
    
    return frames


def is_content_worthy(signal: Signal) -> bool:
    """Check if a signal is worth making content about."""
    # Large change
    if abs(signal.change) > 0.2:
        return True
    
    # High confidence
    if signal.confidence > 0.8:
        return True
    
    # Money implication
    if any(kw in signal.metric.lower() for kw in ['pay', 'salary', 'wage', 'revenue', 'profit', 'value']):
        return True
    
    # Clear action
    if signal.content_frames and ContentFrame.OPPORTUNITY in signal.content_frames:
        return True
    
    return False


def detect_all_signals(canonical_dir: str = None) -> List[Signal]:
    """Detect signals from all canonical observations."""
    if canonical_dir is None:
        canonical_dir = str(Path(__file__).parent.parent / 'canonical')
    
    all_signals = []
    
    # UKOpportunity signals
    opp_dir = Path(canonical_dir) / 'ukopportunity'
    if opp_dir.exists():
        observations = []
        for f in sorted(opp_dir.glob('*.jsonl'), reverse=True)[:7]:
            with open(f) as fh:
                for line in fh:
                    try:
                        observations.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        # Planning signals
        planning_obs = [o for o in observations if o.get('metric') == 'planning_application']
        all_signals.extend(detect_signals_from_planning(planning_obs))
        
        # Contract signals
        contract_obs = [o for o in observations if o.get('metric') == 'contract_award']
        all_signals.extend(detect_signals_from_contracts(contract_obs))
    
    # Score all signals
    for signal in all_signals:
        signal.interestingness = score_signal(signal)
        signal.content_frames = generate_content_frames(signal)
        signal.content_worthy = is_content_worthy(signal)
    
    # Sort by interestingness
    all_signals.sort(key=lambda s: s.interestingness, reverse=True)
    
    return all_signals


if __name__ == '__main__':
    signals = detect_all_signals()
    print(f"Detected {len(signals)} signals")
    for s in signals[:10]:
        print(f"  {s.entity}: {s.metric} = {s.change} (score: {s.interestingness})")
        print(f"    Frames: {[f.value for f in s.content_frames]}")
        print(f"    Content worthy: {s.content_worthy}")
        print()
