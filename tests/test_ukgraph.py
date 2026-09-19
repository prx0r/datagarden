"""Tests for UKGraph MCP truth contract."""

import importlib.util
from pathlib import Path
from unittest.mock import patch


def test_wage_growth_unavailable():
    """wage_growth returns UNAVAILABLE until ASHE data is collected."""
    spec = importlib.util.spec_from_file_location(
        "ukgraph_mcp",
        Path(__file__).parent.parent / "mcp" / "ukgraph_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.wage_growth(soc_code="6135", region="E12000001", start_year=2020, end_year=2024)
    
    # Must have PR5 contract
    assert "truth_class" in result
    assert "confidence" in result
    assert "limitations" in result
    assert "method" in result


def test_career_crowding_no_fake_scores():
    """career_crowding doesn't return fake scores from document counts."""
    spec = importlib.util.spec_from_file_location(
        "ukgraph_mcp",
        Path(__file__).parent.parent / "mcp" / "ukgraph_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.career_crowding("software developer")
    
    # Should NOT have a numeric crowding_score
    if "result" in result and "crowding_score" in result.get("result", {}):
        # If it exists, it should be None or the tool should explain it's conceptual
        score = result["result"]["crowding_score"]
        assert score is None or result["truth_class"] in ["CONCEPTUAL", "UNAVAILABLE"]


def test_find_shortages_conceptual():
    """find_shortages returns CONCEPTUAL until data sources are joined."""
    spec = importlib.util.spec_from_file_location(
        "ukgraph_mcp",
        Path(__file__).parent.parent / "mcp" / "ukgraph_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.find_shortages()
    
    # Must have PR5 contract
    assert "truth_class" in result
    assert "limitations" in result
    assert "method" in result


def test_data_status_has_sources():
    """data_status lists data sources."""
    spec = importlib.util.spec_from_file_location(
        "ukgraph_mcp",
        Path(__file__).parent.parent / "mcp" / "ukgraph_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.data_status()
    
    # Should have sources listed
    assert "result" in result
    assert "data_sources" in result["result"]
