#!/usr/bin/env python3
"""End-to-end pipeline test."""

from content.signals import detect_all_signals
from content.compiler import compile_content_for_signal
from core.normalize import load_observations
from core.source_registry import SourceRegistry

# Step 1: Canonical data
print('=== STEP 1: Canonical Data ===')
import os
total = 0
for garden in ['ukopportunity', 'ukgraph', 'ukadmin', 'breadup', 'powpowpow']:
    path = f'canonical/{garden}'
    if os.path.exists(path):
        for f in os.listdir(path):
            if f.endswith('.jsonl'):
                with open(f'{path}/{f}') as fh:
                    count = sum(1 for _ in fh)
                    total += count
                    print(f'  {garden}/{f}: {count} records')
print(f'  TOTAL: {total} canonical observations')

# Step 2: Source registry
print()
print('=== STEP 2: Source Registry ===')
registry = SourceRegistry()
for source in registry.list_sources():
    print(f'  {source.name}: {source.licence} ({source.recoverability})')

# Step 3: Signal detection
print()
print('=== STEP 3: Signal Detection ===')
signals = detect_all_signals()
print(f'  Detected {len(signals)} signals')
for s in signals[:5]:
    print(f'    {s.entity} {s.metric} = {s.change} (score: {s.interestingness})')
    print(f'      Content worthy: {s.content_worthy}, Frames: {s.content_frames}')

# Step 4: Content compilation
print()
print('=== STEP 4: Content Compilation ===')
for signal in signals[:2]:
    manifests = compile_content_for_signal(signal)
    for m in manifests:
        print(f'  [{m.template}] {m.hook}')
        print(f'    Claim: {m.claim}')
        if m.proof:
            print(f'    Proof: {m.proof[0][:80]}')

# Step 5: Earn endpoint
print()
print('=== STEP 5: Earn Endpoint ===')
from uk_boring.earn import find_earn_opportunities, CapabilityEnvelope
profile = CapabilityEnvelope(
    location='Oldham',
    skills=['electrician'],
    certifications=['NICEIC'],
    capital=500,
)
opps = find_earn_opportunities(profile)
print(f'  {len(opps)} opportunities for electrician in Oldham')
for o in opps[:3]:
    print(f'    {o.action}: {o.title[:50]}')
    print(f'      Value: {o.estimated_value_gbp}, Source: {o.source}')

print()
print('=== PIPELINE COMPLETE ===')
