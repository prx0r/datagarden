"""
UKGraph Content Compiler — turns signals into content manifests.

The pipeline:
signal → content query → graph expansion → content manifest → renderer

Each signal spawns one or more content queries based on its frames.
Each content query expands the graph to find supporting facts.
The content manifest is a deterministic view of the graph.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from core.signal import Signal, ContentQuery, ContentManifest, ContentFrame


def signal_to_queries(signal: Signal) -> List[ContentQuery]:
    """Convert a signal into content queries based on its frames."""
    queries = []
    
    for frame in signal.content_frames:
        if isinstance(frame, ContentFrame):
            frame = frame.value
        
        query = ContentQuery(
            query_id=f"q_{signal.signal_id}_{frame}",
            signal_id=signal.signal_id,
            frame=frame,
            seed_entity=signal.entity,
            seed_metric=signal.metric,
            seed_change=signal.change,
        )
        
        # Set expansion targets based on frame type
        if frame == "CHANGE":
            query.expand_metrics = [signal.metric]
            query.tone = "informative"
            query.max_facts = 3
            
        elif frame == "OPPORTUNITY":
            query.expand_metrics = [signal.metric, "adjacent_demands", "skill_transferability"]
            query.tone = "encouraging"
            query.max_facts = 4
            
        elif frame == "WARNING":
            query.expand_metrics = [signal.metric, "exposure_level", "mitigation_options"]
            query.tone = "urgent"
            query.max_facts = 3
            
        elif frame == "WHERE":
            query.expand_places = [signal.place]
            query.expand_metrics = [signal.metric]
            query.tone = "informative"
            query.max_facts = 4
            
        elif frame == "COMPARE":
            query.expand_metrics = [signal.metric]
            query.tone = "informative"
            query.max_facts = 4
        
        queries.append(query)
    
    return queries


def expand_query_graph(query: ContentQuery, observations: list) -> dict:
    """Expand a content query into supporting graph facts."""
    facts = []
    
    for obs in observations:
        value = obs.get('value', {})
        if not isinstance(value, dict):
            continue
        metric = obs.get('metric', '')
        entity = value.get('description', '') or value.get('reference', '')
        
        # Check relevance
        if query.seed_entity.lower() in entity.lower():
            facts.append({
                "fact_id": obs.get('observation_id', ''),
                "metric": metric,
                "entity": entity,
                "value": value,
                "relevance": "direct",
            })
    
    return {
        "query_id": query.query_id,
        "seed": {
            "entity": query.seed_entity,
            "metric": query.seed_metric,
            "change": query.seed_change,
        },
        "facts": facts[:query.max_facts],
        "fact_count": len(facts),
    }


def compile_content(signal: Signal, query: ContentQuery, expanded: dict) -> ContentManifest:
    """Compile a content manifest from expanded graph facts."""
    facts = expanded.get('facts', [])
    
    # Build claim from signal
    change_pct = round(signal.change * 100)
    if signal.change > 0:
        claim = f"{signal.entity} {signal.metric.replace('_', ' ')} are up {change_pct}% over {signal.window}."
    else:
        claim = f"{signal.entity} {signal.metric.replace('_', ' ')} are down {abs(change_pct)}% over {signal.window}."
    
    # Build proof from facts
    proof = []
    for fact in facts[:3]:
        desc = fact.get('entity', '') or fact.get('metric', '')
        proof.append(desc[:100])
    
    # Build hook based on frame
    if query.frame == "OPPORTUNITY":
        hook = f"What can {signal.entity} do about this?"
    elif query.frame == "WARNING":
        hook = f"Who is exposed to this change in {signal.entity}?"
    elif query.frame == "CHANGE":
        hook = f"Here's what changed about {signal.entity}."
    elif query.frame == "WHERE":
        hook = f"Where is this strongest in {signal.place}?"
    elif query.frame == "COMPARE":
        hook = f"How does {signal.entity} compare?"
    else:
        hook = f"Here's what's happening with {signal.entity}."
    
    # Build close
    close = f"Source: {signal.source_garden}. Confidence: {signal.confidence:.0%}."
    
    return ContentManifest(
        manifest_id=f"cm_{signal.signal_id}_{query.frame}",
        signal_id=signal.signal_id,
        query_id=query.query_id,
        template=query.frame,
        hook=hook,
        claim=claim,
        proof=proof,
        close=close,
        source_ids=signal.evidence,
    )


def compile_content_for_signal(signal: Signal, observations: list = None) -> List[ContentManifest]:
    """Full pipeline: signal → queries → expansion → manifests."""
    # Generate queries from signal
    queries = signal_to_queries(signal)
    
    # Load observations if not provided
    if observations is None:
        observations = _load_all_observations()
    
    manifests = []
    for query in queries:
        # Expand graph
        expanded = expand_query_graph(query, observations)
        
        # Compile content
        manifest = compile_content(signal, query, expanded)
        manifests.append(manifest)
    
    return manifests


def _load_all_observations() -> list:
    """Load all canonical observations."""
    canonical_dir = Path(__file__).parent.parent / 'canonical'
    observations = []
    
    for garden_dir in canonical_dir.iterdir():
        if not garden_dir.is_dir():
            continue
        for f in garden_dir.glob('*.jsonl'):
            with open(f) as fh:
                for line in fh:
                    try:
                        observations.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    return observations


if __name__ == '__main__':
    from content.signals import detect_all_signals
    
    signals = detect_all_signals()
    print(f"Detected {len(signals)} signals\n")
    
    for signal in signals[:3]:
        print(f"Signal: {signal.entity} {signal.metric} = {signal.change}")
        manifests = compile_content_for_signal(signal)
        for m in manifests:
            print(f"  [{m.template}] {m.hook}")
            print(f"    Claim: {m.claim}")
            if m.proof:
                print(f"    Proof: {m.proof[0]}")
            print()
