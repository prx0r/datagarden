"""Tests for normalizer roundtrip — raw data → canonical → load."""

import json
from pathlib import Path
from unittest.mock import patch


def test_normalize_powpowpow_chain():
    """PowPowPow chain data normalizes to canonical form."""
    from shared.normalize import normalize_from_source
    
    raw = {
        "symbol": "XMR",
        "price_usd": 564.55,
        "market_cap": 10400000000,
        "volume_24h": 85000000,
        "hashrate": 5.2e9,
        "difficulty": 324000000000,
    }
    
    record = normalize_from_source("powpowpow", "chain_data", raw)
    
    # Should return a dict with observation fields
    assert isinstance(record, dict)
    assert "observed_at" in record


def test_normalize_ukgraph_ons():
    """UKGraph ONS bulletin normalizes to canonical form."""
    from shared.normalize import normalize_from_source
    
    raw = {
        "title": "UK labour market",
        "summary": "Employment statistics",
        "type": "bulletin",
        "release_date": "2026-08-18",
        "query": "labour market",
    }
    
    record = normalize_from_source("ukgraph", "ons_bulletin", raw)
    
    assert isinstance(record, dict)
    assert "observed_at" in record


def test_normalize_ukadmin_task():
    """UK Admin task normalizes to canonical form."""
    from shared.normalize import normalize_from_source
    
    raw = {
        "task_id": "renew_driving_licence",
        "task_name": "Renew your driving licence",
        "category": "driving",
        "authority": "DVLA",
        "jurisdiction": "GB",
        "url": "https://www.gov.uk/renew-driving-licence",
        "cost_gbp": 14.0,
        "requires": ["identity", "licence_details"],
        "agent_permissions": {"explain": True, "submit": False},
        "last_verified": "2026-09-19",
    }
    
    record = normalize_from_source("ukadmin", "curated_task", raw)
    
    assert isinstance(record, dict)
    assert "observed_at" in record


def test_store_load_roundtrip(tmp_path, monkeypatch):
    """Store observations and load them back."""
    from core.observation import Observation, TruthClass
    import core.storage as storage
    
    monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
    
    obs = Observation(
        observation_id="roundtrip-test",
        entity_id="test-entity",
        garden="test",
        metric="price",
        value=100,
        event_time="2026-09-19T00:00:00Z",
        observed_at="2026-09-19T00:00:00Z",
        source_id="test",
        truth_class=TruthClass.VERIFIED,
    )
    
    storage.store_observation(obs)
    loaded = storage.load_observations("test")
    
    assert len(loaded) == 1
    assert loaded[0]["observation_id"] == "roundtrip-test"
    assert loaded[0]["truth_class"] == "verified"
