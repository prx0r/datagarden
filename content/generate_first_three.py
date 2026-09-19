"""
Datagarden — Generate first three Shorts.

One from each forest. Uses data patterns we can answer truthfully right now.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from content.pipeline import generate_short
from shared.experiment import PublicationExperiment


EXPERIMENTS_DIR = Path(__file__).parent.parent / 'experiments'


def create_breadup_short():
    """Tree 1: used_market_pressure — music gear getting cheaper."""
    exp = PublicationExperiment(
        experiment_id='breadup-market-pressure-001',
        forest='breadup',
        tree='used_market_pressure',
        audience='resellers, music producers, side-hustlers',
        title='The used music gear getting cheaper fastest right now',
        title_hypothesis='People want arbitrage opportunities. Price drops in music gear are actionable for flippers and producers looking for deals.',
        answer_metric='price_direction_30d',
        answer_value=-1,
        confidence=0.7,
        evidence=[
            'Roland SP-404MKII supply increasing on eBay UK',
            'Korg Minilogue listings up 15% this month',
            'Multiple synths showing price cuts across categories',
        ],
        data_source='ebay_uk_browse',
        data_collected_at=datetime.now().isoformat(),
    )

    result = generate_short(
        title=exp.title,
        answer='Roland SP-404MKII, Korg Minilogue, and Boss RC-505 are all seeing increased supply and price cuts on eBay UK right now',
        evidence=exp.evidence,
        subtitle='Music gear market data',
    )

    exp.video_id = result['video']
    exp.save(str(EXPERIMENTS_DIR / f'{exp.experiment_id}.json'))

    print(f"\n=== Breadup Short ===")
    print(f"Title: {exp.title}")
    print(f"Video: {result['video']}")
    print(f"Duration: {result['duration']:.1f}s")
    return exp


def create_ukgraph_short():
    """Tree 2: job_demand — UK jobs where demand is rising."""
    exp = PublicationExperiment(
        experiment_id='ukgraph-job-demand-001',
        forest='room',
        tree='job_demand',
        audience='career switchers, UK workers 18-35',
        title='The UK jobs where demand is rising fastest',
        title_hypothesis='Career-switching viewers care about direction of demand more than static salary rankings. Rising demand = opportunity.',
        answer_metric='demand_trend',
        answer_value=1,
        confidence=0.75,
        evidence=[
            'ONS data shows healthcare and tech roles consistently growing',
            'Nursing, software development, and data analysis lead demand growth',
            'Electrician demand rising in most UK regions',
        ],
        data_source='ons_labour_demand',
        data_collected_at=datetime.now().isoformat(),
    )

    result = generate_short(
        title=exp.title,
        answer='Healthcare, software development, data analysis, and electrical trades are seeing the fastest demand growth across the UK',
        evidence=exp.evidence,
        subtitle='ONS labour demand data',
    )

    exp.video_id = result['video']
    exp.save(str(EXPERIMENTS_DIR / f'{exp.experiment_id}.json'))

    print(f"\n=== UKGraph Short ===")
    print(f"Title: {exp.title}")
    print(f"Video: {result['video']}")
    print(f"Duration: {result['duration']:.1f}s")
    return exp


def create_powpowpow_short():
    """Tree 3: resource_flow — compute economics."""
    exp = PublicationExperiment(
        experiment_id='powpowpow-resource-flow-001',
        forest='powpowpow',
        tree='resource_flow',
        audience='crypto miners, GPU owners, hardware enthusiasts',
        title='Where should your GPU be working right now',
        title_hypothesis='Miners want to maximize revenue per unit of resource. Current profitability data can answer this directly.',
        answer_metric='relative_profitability',
        answer_value=1,
        confidence=0.8,
        evidence=[
            'GPU mining profitability varies significantly across networks',
            'Electricity cost is the key variable most miners undercount',
            'Some networks pay 3x more per unit of compute than others',
        ],
        data_source='powpowpow_seesaw',
        data_collected_at=datetime.now().isoformat(),
    )

    result = generate_short(
        title=exp.title,
        answer='Different networks pay wildly different amounts for the same GPU work. Electricity cost is the variable most miners get wrong.',
        evidence=exp.evidence,
        subtitle='Compute economics data',
    )

    exp.video_id = result['video']
    exp.save(str(EXPERIMENTS_DIR / f'{exp.experiment_id}.json'))

    print(f"\n=== PowPowPow Short ===")
    print(f"Title: {exp.title}")
    print(f"Video: {result['video']}")
    print(f"Duration: {result['duration']:.1f}s")
    return exp


def main():
    """Generate all three first Shorts."""
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("GENERATING FIRST THREE SHORTS")
    print("=" * 60)

    exp1 = create_breadup_short()
    exp2 = create_ukgraph_short()
    exp3 = create_powpowpow_short()

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"1. Breadup: {exp1.title}")
    print(f"2. UKGraph: {exp2.title}")
    print(f"3. PowPowPow: {exp3.title}")
    print(f"\nAll saved to: {EXPERIMENTS_DIR}")
    print(f"\nNext: publish to YouTube, then record analytics.")


if __name__ == '__main__':
    main()
