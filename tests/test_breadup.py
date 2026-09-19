"""Tests for Breadup MCP truth contract."""

import json
from pathlib import Path


def test_value_listing_contract_fields():
    """value_listing returns the PR5 contract fields."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "breadup_mcp", 
        Path(__file__).parent.parent / "mcp" / "breadup_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.value_listing("test item", 100.0)
    
    # Must have all PR5 contract fields
    assert "capability" in result
    assert "truth_class" in result
    assert "confidence" in result
    assert "evidence" in result
    assert "method" in result
    assert "limitations" in result
    assert "action" in result
    assert result["capability"] == "breadup.value_listing"


def test_max_offer_contract():
    """max_offer returns the PR5 contract."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "breadup_mcp",
        Path(__file__).parent.parent / "mcp" / "breadup_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.max_offer("test item")
    
    assert "truth_class" in result
    assert "limitations" in result
    assert "method" in result


def test_liquidity_score_contract():
    """liquidity_score returns the PR5 contract."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "breadup_mcp",
        Path(__file__).parent.parent / "mcp" / "breadup_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.liquidity_score("test item")
    
    assert "truth_class" in result
    assert "limitations" in result


def test_repair_vs_sell_honest():
    """repair_vs_sell admits assumptions."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "breadup_mcp",
        Path(__file__).parent.parent / "mcp" / "breadup_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.repair_vs_sell("test item", "broken screen")
    
    # Should be UNAVAILABLE (no data) or HEURISTIC (has data but uses assumptions)
    assert result["truth_class"] in ["UNAVAILABLE", "HEURISTIC"]
    assert "method" in result
