"""Move Home workflow — the first complete UK Boring chain.

"I moved yesterday, sort everything"

This is the proof of concept. One complete life-event graph
that demonstrates the full architecture.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class WorkflowStep:
    step_id: str
    name: str
    description: str
    action_class: str        # AUTO, PREPARE, APPROVAL_REQUIRED, USER_HANDOFF
    execution_mode: str      # api, browser, auth_browser, handoff, offline
    depends_on: list = field(default_factory=list)  # step_ids
    required_info: list = field(default_factory=list)
    official_url: str = ""
    estimated_time: str = ""
    receipt_pattern: dict = field(default_factory=dict)

@dataclass
class MoveHomeWorkflow:
    """Complete move-home workflow.

    Input: person moving, old_address, new_address, move_date
    Output: all administrative changes completed
    """
    workflow_id: str = "move_home"
    name: str = "Move Home"
    description: str = "Update all government and service records when moving house"

    # Required inputs
    required_inputs: list = field(default_factory=lambda: [
        "move_date",
        "old_address",
        "new_address",
        "full_name",
    ])

    # Optional inputs
    optional_inputs: list = field(default_factory=lambda: [
        "council_tax_reference",
        "vehicle_registration",
        "national_insurance_number",
    ])

    # The steps
    steps: list = field(default_factory=list)

    def __post_init__(self):
        if not self.steps:
            self.steps = self._default_steps()

    def _default_steps(self):
        return [
            WorkflowStep(
                step_id="resolve_place",
                name="Resolve new place",
                description="Look up UPRN/postcode → council, services, applicable rules",
                action_class="AUTO",
                execution_mode="api",
                depends_on=[],
                required_info=["new_postcode"],
            ),
            WorkflowStep(
                step_id="council_tax_move",
                name="Notify council tax",
                description="Tell Oldham Council about the move",
                action_class="APPROVAL_REQUIRED",
                execution_mode="browser",
                depends_on=["resolve_place"],
                required_info=["council_tax_reference", "move_date", "new_address"],
                official_url="https://www.oldham.gov.uk/info/200198/council_tax/1406/changing_address",
                receipt_pattern={
                    "type": "confirmation_page",
                    "fields": [
                        {"name": "reference", "exists": True},
                        {"name": "status", "contains": "updated"},
                    ],
                },
            ),
            WorkflowStep(
                step_id="dvla_address",
                name="Update driving licence address",
                description="Change address on DVLA driving licence",
                action_class="APPROVAL_REQUIRED",
                execution_mode="browser",
                depends_on=["resolve_place"],
                required_info=["full_name", "new_address"],
                official_url="https://www.gov.uk/change-address-driving-licence",
                receipt_pattern={
                    "type": "confirmation_page",
                    "fields": [
                        {"name": "reference", "pattern": "DL-\\d{4}-\\d{5}"},
                        {"name": "status", "contains": "application"},
                    ],
                },
            ),
            WorkflowStep(
                step_id="electoral_register",
                name="Register at new address",
                description="Register to vote at new address",
                action_class="USER_HANDOFF",
                execution_mode="browser",
                depends_on=["resolve_place"],
                required_info=["full_name", "new_address", "national_insurance_number"],
                official_url="https://www.gov.uk/register-to-vote",
                receipt_pattern={
                    "type": "confirmation_page",
                    "fields": [
                        {"name": "reference", "exists": True},
                        {"name": "status", "contains": "registered"},
                    ],
                },
            ),
            WorkflowStep(
                step_id="hmrc_address",
                name="Update HMRC address",
                description="Notify HMRC of new address for tax purposes",
                action_class="USER_HANDOFF",
                execution_mode="browser",
                depends_on=[],
                required_info=["full_name", "new_address"],
                official_url="https://www.gov.uk/log-in-register-hmrc-online-services",
            ),
            WorkflowStep(
                step_id="vehicle_tax",
                name="Update vehicle tax address",
                description="Update address on DVLA vehicle tax",
                action_class="APPROVAL_REQUIRED",
                execution_mode="browser",
                depends_on=["resolve_place"],
                required_info=["vehicle_registration", "new_address"],
                official_url="https://www.gov.uk/vehicle-tax",
                receipt_pattern={
                    "type": "confirmation_page",
                    "fields": [
                        {"name": "vehicle_registration", "exists": True},
                        {"name": "tax_status", "one_of": ["taxed", "SORN"]},
                    ],
                },
            ),
        ]

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "required_inputs": self.required_inputs,
            "optional_inputs": self.optional_inputs,
            "steps": [
                {
                    "step_id": s.step_id,
                    "name": s.name,
                    "description": s.description,
                    "action_class": s.action_class,
                    "execution_mode": s.execution_mode,
                    "depends_on": s.depends_on,
                    "official_url": s.official_url,
                    "receipt_pattern": s.receipt_pattern,
                }
                for s in self.steps
            ],
        }
