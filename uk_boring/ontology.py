"""The 12 core ontology objects.

Everything in UK Boring decomposes into these:
  Place, Service, Rule, Workflow, Form, Requirement,
  Evidence, Action, Outcome, Provider, Offer, Signal
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Service:
    """A government or local service available at a Place."""
    service_id: str
    name: str
    authority: str            # who provides it
    category: str             # council_tax, waste, housing, etc.
    url: str = ""             # official URL
    cost_gbp: float = 0
    requires_auth: bool = False
    agent_accessible: bool = True
    description: str = ""

@dataclass
class Rule:
    """A deterministic rule that applies at a Place."""
    rule_id: str
    service_id: str
    description: str
    condition: str            # human-readable condition
    code: str = ""            # machine-readable rule
    effective_from: str = ""
    effective_to: str = ""
    source_url: str = ""

@dataclass
class Requirement:
    """What's needed for a workflow step."""
    requirement_id: str
    description: str
    type: str                 # identity, document, information, payment
    optional: bool = False
    default_value: str = ""
    validation: str = ""      # regex or rule

@dataclass
class Form:
    """A form that needs to be filled."""
    form_id: str
    service_id: str
    name: str
    url: str
    method: str               # api, browser, auth_browser, handoff, offline
    fields: list = field(default_factory=list)  # list of Requirement
    auth_required: bool = False

@dataclass
class Evidence:
    """An observation with source and timestamp."""
    evidence_id: str
    metric: str
    value: str
    unit: str = ""
    source: str = ""
    observed_at: str = ""

@dataclass
class Action:
    """An execution step in a workflow."""
    action_id: str
    workflow_id: str
    description: str
    action_class: str          # AUTO, PREPARE, APPROVAL_REQUIRED, USER_HANDOFF, UNSUPPORTED
    execution_mode: str        # api, browser, auth_browser, handoff, offline
    form_id: str = ""
    requires_approval: bool = False
    estimated_time: str = ""

@dataclass
class Outcome:
    """What actually happened after an action."""
    outcome_id: str
    action_id: str
    status: str               # SUCCESS, PARTIAL, FAILURE, PENDING
    evidence: list = field(default_factory=list)  # list of Evidence
    receipt_data: dict = field(default_factory=dict)
    observed_at: str = ""

@dataclass
class Provider:
    """A local provider (business, tradesperson, etc.)."""
    provider_id: str
    name: str
    category: str             # removals, broadband, insurance, etc.
    area: str                 # postcode area or LA
    url: str = ""
    rating: float = 0
    verified: bool = False

@dataclass
class Offer:
    """A commercial offer attached to a workflow."""
    offer_id: str
    provider_id: str
    workflow_id: str
    description: str
    price_gbp: float = 0
    url: str = ""
    affiliate: bool = False

@dataclass
class Signal:
    """A detected change or pattern in a Place."""
    signal_id: str
    place_id: str
    signal_type: str           # economic, regulatory, demographic, commercial
    description: str
    strength: float = 0        # 0-1
    detected_at: str = ""
    source: str = ""
