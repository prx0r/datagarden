"""
UKGraph Jev Signal Ranker — uses Jev via OpenRouter for semantic classification.

From the architecture:
"Jev is the semantic compressor."
"Jev chooses; code executes."

This module calls Jev to rank/classify/gate signals for content generation.
"""

import json
import os
import requests
from pathlib import Path
from typing import List, Optional, Dict


OPENROUTER_KEY = None
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
JEV_DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"


def _get_key() -> Optional[str]:
    """Get OpenRouter API key from agentvault or environment."""
    global OPENROUTER_KEY
    if OPENROUTER_KEY:
        return OPENROUTER_KEY
    
    # Try agent vault
    try:
        from agent_vault import get_key
        OPENROUTER_KEY = get_key('openrouter')
        if OPENROUTER_KEY:
            return OPENROUTER_KEY
    except Exception:
        pass
    
    # Try environment
    OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY')
    return OPENROUTER_KEY


def rank_signals_jev(signals: list, max_results: int = 10) -> list:
    """Use Jev to rank signals for content worthiness.
    
    For each signal, Jev answers:
    - Is this materially interesting? (score 0-10)
    - Which audience is most affected? (choice)
    - Which framing fits best? (choice)
    - Is there an actionable monetary implication? (noul)
    """
    key = _get_key()
    if not key:
        # Fallback: use deterministic scoring
        return _rank_signals_deterministic(signals, max_results)
    
    ranked = []
    for signal in signals[:50]:  # Limit to top 50 candidates
        
        state = json.dumps({
            "signal": {
                "entity": signal.entity,
                "place": signal.place,
                "metric": signal.metric,
                "change": signal.change,
                "window": signal.window,
                "confidence": signal.confidence,
                "related": signal.related,
            }
        })
        
        questions = {
            "interest": {
                "type": "score",
                "min": 0,
                "max": 10,
                "instructions": "How interesting is this for a general UK audience? 0=boring, 10=cannot ignore"
            },
            "frame": {
                "type": "choice",
                "instructions": "Which content frame fits best?",
                "criteria": {
                    "job_stress": "This threatens jobs or livelihoods",
                    "retraining": "People should learn new skills because of this",
                    "opportunity": "There is money or advantage to be gained",
                    "geographic": "This varies strongly by UK region",
                    "comparison": "This compares two things meaningfully",
                    "warning": "People are at risk from this"
                }
            },
            "money": {
                "type": "noul",
                "instructions": "Does this have a clear monetary implication someone could act on?"
            },
            "audience": {
                "type": "choice",
                "instructions": "Which audience segment is most affected?",
                "criteria": {
                    "workers": "People in affected jobs",
                    "businesses": "Companies in the sector",
                    "career_switchers": "People considering changing careers",
                    "investors": "People with capital",
                    "general": "Broad UK audience"
                }
            }
        }
        
        payload = {
            "model": JEV_MODEL,
            "state": state,
            "questions": {
                "interest": {
                    "type": "score",
                    "min": 0,
                    "max": 10,
                    "instructions": "How interesting is this for a general UK audience? 0=boring, 10=cannot ignore"
                },
                "frame": {
                    "type": "choice",
                    "instructions": "Which content frame fits best?",
                    "criteria": {
                        "job_stress": "This threatens jobs or livelihoods",
                        "retraining": "People should learn new skills because of this",
                        "opportunity": "There is money or advantage to be gained",
                        "geographic": "This varies strongly by UK region",
                        "comparison": "This compares two things meaningfully",
                        "warning": "People are at risk from this"
                    }
                },
                "money": {
                    "type": "noul",
                    "instructions": "Does this have a clear monetary implication someone could act on?"
                },
                "audience": {
                    "type": "choice",
                    "instructions": "Which audience segment is most affected?",
                    "criteria": {
                        "workers": "People in affected jobs",
                        "businesses": "Companies in the sector",
                        "career_switchers": "People considering changing careers",
                        "investors": "People with capital",
                        "general": "Broad UK audience"
                    }
                }
            }
        }
        
        try:
            resp = requests.post(
                JEV_DECISIONS_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10,
            )
            
            if resp.status_code == 200:
                data = resp.json()
                # Parse Jev decisions response
                answers = data.get('answers', data)
                
                # Extract interest score
                interest = answers.get('interest', {})
                if isinstance(interest, dict):
                    signal.interestingness = interest.get('score', 5) / 10.0
                elif isinstance(interest, (int, float)):
                    signal.interestingness = interest / 10.0
                else:
                    signal.interestingness = _score_deterministic(signal)
                
                # Extract frame
                frame = answers.get('frame', {})
                if isinstance(frame, dict):
                    signal.content_frames = [frame.get('choice', 'OPPORTUNITY')]
                elif isinstance(frame, str):
                    signal.content_frames = [frame]
                else:
                    signal.content_frames = ['OPPORTUNITY']
                
                # Extract money implication
                money = answers.get('money', {})
                if isinstance(money, dict):
                    signal.content_worthy = money.get('noul', False)
                elif isinstance(money, bool):
                    signal.content_worthy = money
                else:
                    signal.content_worthy = signal.interestingness > 0.5
                
                signal._jev_answers = answers
            else:
                signal.interestingness = _score_deterministic(signal)
                signal.content_worthy = signal.interestingness > 0.5
        except Exception as e:
            signal.interestingness = _score_deterministic(signal)
            signal.content_worthy = signal.interestingness > 0.5
        
        ranked.append(signal)
    
    # Sort by interestingness
    ranked.sort(key=lambda s: s.interestingness, reverse=True)
    return ranked[:max_results]


def _rank_signals_deterministic(signals: list, max_results: int) -> list:
    """Fallback: rank signals without Jev."""
    for signal in signals:
        signal.interestingness = _score_deterministic(signal)
        signal.content_worthy = signal.interestingness > 0.5
    
    signals.sort(key=lambda s: s.interestingness, reverse=True)
    return signals[:max_results]


def _score_deterministic(signal) -> float:
    """Deterministic signal scoring."""
    magnitude = min(abs(signal.change) / 10.0, 1.0)
    confidence = signal.confidence
    novelty = 0.5
    human_relevance = 0.7
    actionability = 0.6
    return round(magnitude * confidence * novelty * human_relevance * actionability, 3)


if __name__ == '__main__':
    from content.signals import detect_all_signals
    
    signals = detect_all_signals()
    print(f"Ranking {len(signals)} signals with Jev...\n")
    
    ranked = rank_signals_jev(signals, max_results=5)
    
    for i, s in enumerate(ranked, 1):
        print(f"{i}. {s.entity} {s.metric} = {s.change}")
        print(f"   Interestingness: {s.interestingness}")
        print(f"   Content worthy: {s.content_worthy}")
        print(f"   Frames: {s.content_frames}")
        if hasattr(s, '_jev_answers'):
            print(f"   Jev: {json.dumps(s._jev_answers, indent=2)[:200]}")
        print()
