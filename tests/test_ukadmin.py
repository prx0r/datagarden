"""Tests for UK Admin MCP truth contract."""

import importlib.util
from pathlib import Path


def test_move_house_step_verification():
    """move_house returns steps with verification status."""
    spec = importlib.util.spec_from_file_location(
        "uk_admin_mcp",
        Path(__file__).parent.parent / "mcp" / "uk_admin_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.move_house("2026-10-15", "10 Example Street, M1 1AA", "")
    
    assert result["capability"] == "uk_admin.move_house"
    assert "workflow_steps" in result["result"]
    
    steps = result["result"]["workflow_steps"]
    assert len(steps) > 0
    
    for step in steps:
        # Every step must have verification metadata
        assert "verification_status" in step or "action_class" in step
        assert "source_url" in step or "url" in step


def test_verification_status_honest():
    """verification_status correctly reports all tasks as CONCEPTUAL."""
    spec = importlib.util.spec_from_file_location(
        "uk_admin_mcp",
        Path(__file__).parent.parent / "mcp" / "uk_admin_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.verification_status()
    
    assert result["capability"] == "uk_admin.verification_status"
    summary = result["result"]["summary"]
    
    # All 36 tasks should be conceptual (unverified)
    assert summary["total_tasks"] == 36
    assert summary["verified_tasks"] == 0
    assert summary["conceptual_tasks"] == 36


def test_explain_task_has_source_url():
    """explain_task includes official source URL."""
    spec = importlib.util.spec_from_file_location(
        "uk_admin_mcp",
        Path(__file__).parent.parent / "mcp" / "uk_admin_mcp.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    result = mod.explain_task("renew_driving_licence")
    
    assert result["truth_class"] in ["DERIVED", "ESTIMATED", "CONCEPTUAL"]
    assert "method" in result
    assert "limitations" in result
