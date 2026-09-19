"""Tests for core observation, entity, and storage modules."""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from core.observation import Observation, TruthClass, Recoverability
from core.entity import Entity
from core.derived import DerivedFact
from core.capability import CapabilityResult, ActionClass
from core.outcome import Outcome, OutcomeStatus


class TestObservation:
    def test_deterministic_id(self):
        """Same inputs produce same ID."""
        obs1 = Observation(
            observation_id="",
            entity_id="test-entity",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test-source",
        )
        obs2 = Observation(
            observation_id="",
            entity_id="test-entity",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test-source",
        )
        assert obs1.observation_id == obs2.observation_id

    def test_different_inputs_different_id(self):
        """Different inputs produce different IDs."""
        obs1 = Observation(
            observation_id="",
            entity_id="entity-1",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test-source",
        )
        obs2 = Observation(
            observation_id="",
            entity_id="entity-2",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test-source",
        )
        assert obs1.observation_id != obs2.observation_id

    def test_to_dict_roundtrip(self):
        """Observation serializes and deserializes correctly."""
        obs = Observation(
            observation_id="test-123",
            entity_id="entity-1",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test-source",
            truth_class=TruthClass.VERIFIED,
        )
        d = obs.to_dict()
        assert d["observation_id"] == "test-123"
        assert d["truth_class"] == "verified"
        assert d["entity_id"] == "entity-1"

    def test_truth_class_enum(self):
        """All truth classes are defined."""
        assert TruthClass.VERIFIED.value == "verified"
        assert TruthClass.DERIVED.value == "derived"
        assert TruthClass.ESTIMATED.value == "estimated"
        assert TruthClass.HEURISTIC.value == "heuristic"
        assert TruthClass.CONCEPTUAL.value == "conceptual"
        assert TruthClass.UNAVAILABLE.value == "unavailable"

    def test_recoverability_enum(self):
        """All recoverability classes are defined."""
        assert Recoverability.CANONICAL.value == "canonical"
        assert Recoverability.THIRD_PARTY.value == "third_party"
        assert Recoverability.EPHEMERAL.value == "ephemeral"


class TestEntity:
    def test_entity_creation(self):
        """Entity can be created with required fields."""
        e = Entity(
            entity_id="btc",
            garden="powpowpow",
            entity_type="chain",
            name="Bitcoin",
        )
        assert e.entity_id == "btc"
        assert e.status == "active"

    def test_superseded_entity(self):
        """Superseded entity references successor."""
        e = Entity(
            entity_id="old-entity",
            garden="test",
            entity_type="item",
            name="Old Name",
            status="superseded",
            superseded_by="new-entity",
        )
        assert e.status == "superseded"
        assert e.superseded_by == "new-entity"


class TestCapabilityResult:
    def test_response_contract(self):
        """CapabilityResult follows the PR5 contract."""
        result = CapabilityResult(
            result_id="test-result",
            capability="test.tool",
            garden="test",
            result={"value": 100},
            truth_class=TruthClass.DERIVED,
            confidence=0.85,
            evidence_observation_ids=["obs-1", "obs-2"],
            method_id="test_method",
            method_version="1.0",
            action_class=ActionClass.ADVISORY,
            as_of="2026-09-19T00:00:00Z",
            computed_at="2026-09-19T00:00:00Z",
            limitations=["Test limitation"],
        )
        d = result.to_dict()
        assert d["capability"] == "test.tool"
        assert d["truth_class"] == "derived"
        assert d["confidence"] == 0.85
        assert len(d["evidence_observation_ids"]) == 2
        assert d["action_class"] == "advisory"
        assert len(d["limitations"]) == 1


class TestOutcome:
    def test_pending_outcome(self):
        """Outcome starts as PENDING."""
        o = Outcome(
            outcome_id="out-1",
            capability_result_id="res-1",
            status=OutcomeStatus.PENDING,
        )
        assert o.status == OutcomeStatus.PENDING
        assert o.resolved_at == ""


class TestStorage:
    def test_store_and_load(self, tmp_path, monkeypatch):
        """Can store and load observations."""
        import core.storage as storage
        monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
        
        obs = Observation(
            observation_id="test-obs",
            entity_id="entity-1",
            garden="test",
            metric="price",
            value=100,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test",
        )
        
        obs_id = storage.store_observation(obs)
        assert obs_id == "test-obs"
        
        loaded = storage.load_observations("test")
        assert len(loaded) == 1
        assert loaded[0]["observation_id"] == "test-obs"

    def test_search_observations(self, tmp_path, monkeypatch):
        """Can search observations by query."""
        import core.storage as storage
        monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
        
        obs = Observation(
            observation_id="search-test",
            entity_id="technics-turntable",
            garden="breadup",
            metric="price",
            value=250,
            event_time="2026-09-19T00:00:00Z",
            observed_at="2026-09-19T00:00:00Z",
            source_id="test",
        )
        storage.store_observation(obs)
        
        results = storage.search_observations("breadup", "technics")
        assert len(results) >= 1
        assert results[0]["entity_id"] == "technics-turntable"
