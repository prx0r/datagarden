"""UKBoring Garden Contract.

Mission: Turn annoying UK processes into verifiable outcomes.

Routes it materially improves:
- do() returns workflow with execution steps
- cancel, renew, move, book, respond
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum


class Frequency(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVENT = "event"


@dataclass(frozen=True)
class GardenContract:
    """Garden Contract for UKBoring.

    Hard rule: No Garden Contract without at least one Route it materially improves.
    """

    name: str = "UKBoring"

    user_goal_enabled: tuple[str, ...] = (
        "do -- Deal with this annoying thing (cancel, renew, move, book, "
        "respond, claim, change, report).",
        "watch -- Tell me when a deadline or status changes.",
    )

    raw_sources: tuple[str, ...] = (
        "government_portal_semantics",
        "service_provider_cancellation_policies",
        "council_process_documentation",
        "statutory_requirements_and_deadlines",
        "booking_system_entry_points",
        "refund_and_complaint_procedures",
        "permit_and_licence_application_rules",
        "verified_outcome_reports_from_prior_actions",
    )

    unique_transformation: str = (
        "Maintain a semantic layer for UK administrative workflows: goal, "
        "authority, material constraints, acceptable completion evidence, "
        "failure/handoff conditions, and currently verified exit paths. "
        "Do not model every click -- let frontier agents handle volatile "
        "interfaces. Store only the stable semantic structure an agent needs "
        "to navigate the workflow and verify its outcome. "
        "The asset is not 'here is the cancellation page' -- it is 'for this "
        "billing state, this is the currently verified exit path, and this "
        "evidence proves the subscription is actually terminated.'"
    )

    historical_state_retained: str = (
        "Workflow route changes over time (which path worked last quarter "
        "vs. now). Common failure paths and their resolutions. Retention "
        "offers observed during cancellation flows. Refund outcomes and "
        "amounts. Time from initiation to confirmed completion per workflow "
        "type and authority. Channel differences (phone vs. online vs. in "
        "person) and their success rates. Evidence requirements that changed "
        "over time."
    )

    snapshot_or_event_frequency: str = (
        "Weekly validation of active workflow semantic contracts against "
        "source authorities. Event-driven updates when failure reports "
        "indicate a workflow path has changed. Monthly re-aggregation of "
        "completion time distributions and success rates. Quarterly review "
        "of all active BoringGoals for continued relevance."
    )

    outputs: tuple[str, ...] = (
        "Route(route_type in {CANCELLATION, RENEWAL, BOOKING, ADMIN, SAVING, REFUND})",
        "BoringGoal(workflow semantic contract)",
        "WorkflowExecutionPlan(goal, execution_class, steps)",
        "CompletionProof(goal) -> acceptable evidence types",
        "WorkflowOutcomeHistory(goal, authority) -> success_rate, time_to_complete, common_failures",
    )

    proof_loop: str = (
        "Route offered (e.g. cancel subscription) -> agent navigates to "
        "authoritative entrypoint, executes steps -> external evidence "
        "collected (cancellation confirmation email, account status change, "
        "refund received) -> Receipt settles TRUE/FALSE/UNKNOWN from external "
        "evidence, not agent assertion -> outcome updates completion time "
        "distribution, success rate, and failure path knowledge for this "
        "goal-authority pair -> future Routes re-weighted by verified "
        "historical success."
    )

    failure_modes: tuple[str, ...] = (
        "SOURCE_DOWN -- government or service provider portal unreachable",
        "SOURCE_SCHEMA_CHANGED -- portal workflow changed, semantic contract "
        "no longer matches reality",
        "AUTH_REQUIRED -- workflow requires human authentication or MFA that "
        "agent cannot complete",
        "HUMAN_ONLY -- current route cannot be completed agentically, "
        "requires personal presence or phone call",
        "EVIDENCE_AMBIGUOUS -- completion evidence is unclear or could be "
        "interpreted multiple ways",
        "WORKFLOW_DRIFT -- authority changed the process but semantic "
        "contract was not updated, leading to agent following obsolete path",
        "RETENTION_TRAP -- cancellation flow designed to be confusing, "
        "agent navigates into retention funnel instead of completing goal",
        "PROOF_MISSING -- action completed but no verifiable external "
        "evidence exists to settle the Receipt",
    )

    irrecoverable_asset: str = (
        "Historical workflow outcome data: which paths actually succeeded, "
        "how long they took, what evidence proved completion, what failures "
        "were encountered, and how the process changed over time. Once a "
        "service provider alters their cancellation flow, only our retained "
        "record preserves what worked before the change. Actual cancellation "
        "success/failure paths over time cannot be reconstructed from "
        "tomorrow's live web. This accumulated workflow truth is the deepest "
        "moat."
    )

    expected_maintenance: str = (
        "Source validation as government portals and service provider "
        "workflows change (estimated 10-20 active workflows requiring "
        "monthly health checks). Semantic contract updates when authorities "
        "modify processes. Proof rule calibration as evidence formats change "
        "(e.g. confirmation email format). Failure path knowledge base "
        "maintenance from new receipt evidence. Quarterly review of "
        "execution class assignments (AUTO/APPROVAL/AUTH_HANDOFF/"
        "DECLARATION/HUMAN_ONLY) against current reality."
    )

    source_licences: tuple[str, ...] = (
        "Government open data (OGL 3.0) for statutory requirements, "
        "deadlines, and official process documentation.",
        "Service provider public-facing terms and conditions -- extraction "
        "of cancellation and refund policies.",
        "Council published procedures -- public information.",
        "No personal data retained. Workflow knowledge is about the "
        "process, not the person performing it.",
    )

    acceptance_tests: tuple[str, ...] = (
        "TEST_WORKFLOW_EXISTS: do() returns a Route with route_type "
        "CANCELLATION, BOOKING, or ADMIN for a valid BoringGoal "
        "(e.g. CANCEL_SERVICE for a known UK broadband provider).",
        "TEST_ROUTE_HAS_EXECUTION_CLASS: Every returned Route includes an "
        "execution_class (AUTO, APPROVAL, AUTH_HANDOFF, DECLARATION, or "
        "HUMAN_ONLY) that reflects the current reality of the workflow.",
        "TEST_ROUTE_HAS_STEPS: Every Route includes an execution plan with "
        "an authoritative_entrypoint and at least one concrete step, "
        "sufficient for a personal agent to initiate action.",
        "TEST_ROUTE_HAS_EVIDENCE: Every Route includes acceptable_proofs "
        "listing the external evidence types that would settle completion "
        "(e.g. confirmation_email, account_status_change, refund_receipt).",
        "TEST_COMPLETION_PROOF: A Route for a workflow with at least one "
        "prior verified completion includes a CompletionProof that specifies "
        "the proof_rule and evidence format sufficient to settle TRUE.",
        "TEST_PROOF_LOOP: A Route that was acted upon has a Receipt with "
        "result TRUE or FALSE settled from external evidence within 7 days "
        "of action, not from the agent's own assertion.",
        "TEST_OUTCOME_HISTORY: For a BoringGoal with 10+ verified outcomes, "
        "WorkflowOutcomeHistory returns a success_rate, median "
        "time_to_complete, and at least one common_failure entry.",
        "TEST_WORKFLOW_DRIFT_DETECTION: When a source fingerprint changes "
        "for an active BoringGoal, a semantic diff is generated and the "
        "contract is flagged for review within 48 hours.",
        "TEST_HUMAN_HANDOFF: A workflow requiring authentication "
        "(AUTH_HANDOFF) correctly identifies the handoff point and provides "
        "clear instructions for the human to complete before the agent "
        "resumes.",
    )
