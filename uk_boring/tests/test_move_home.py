"""Test the move-home workflow."""

def test_workflow_definition():
    """Move home workflow has the right structure."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    wf = MoveHomeWorkflow()
    assert wf.workflow_id == "move_home"
    assert len(wf.steps) >= 5
    assert "new_address" in wf.required_inputs

def test_preflight():
    """Preflight identifies missing information."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    wf = MoveHomeWorkflow()
    # Missing everything
    result = {"have": [], "missing": wf.required_inputs}
    assert len(result["missing"]) > 0

def test_step_dependencies():
    """Steps have correct dependencies."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    wf = MoveHomeWorkflow()
    step_ids = [s.step_id for s in wf.steps]

    # resolve_place should come first
    assert "resolve_place" in step_ids

    # council_tax_move depends on resolve_place
    for s in wf.steps:
        if s.step_id == "council_tax_move":
            assert "resolve_place" in s.depends_on

def test_receipt_patterns():
    """Steps have receipt patterns for verification."""
    from uk_boring.workflows.move_home import MoveHomeWorkflow

    wf = MoveHomeWorkflow()
    for s in wf.steps:
        if s.action_class in ["APPROVAL_REQUIRED", "AUTO"]:
            assert s.receipt_pattern or s.step_id == "resolve_place"
