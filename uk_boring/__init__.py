"""UK Boring — UK local government, decomposed.

Core exports: Place, geo resolvers, ontology objects, and place definitions.
"""

from uk_boring.place import Place
from uk_boring.geo import resolve_postcode, resolve_uprn, get_nearest_postcodes
from uk_boring.ontology import (
    Service,
    Rule,
    Requirement,
    Form,
    Evidence,
    Action,
    Outcome,
    Provider,
    Offer,
    Signal,
    Goal,
    Opportunity,
)
from uk_boring.oldham import OLDHAM, OLDHAM_SERVICES, OLDHAM_LOCAL_WORKFLOWS
from uk_boring.national import (
    NationalWorkflow,
    NATIONAL_WORKFLOWS,
    get_national_workflow,
    list_national_workflows,
)
from uk_boring.goals import GOALS, get_goal, list_goals
from uk_boring.opportunity import (
    process_planning_signal,
    process_business_signal,
    process_contract_signal,
    signals_to_opportunities,
)

__all__ = [
    "Place",
    "resolve_postcode",
    "resolve_uprn",
    "get_nearest_postcodes",
    "Service",
    "Rule",
    "Requirement",
    "Form",
    "Evidence",
    "Action",
    "Outcome",
    "Provider",
    "Offer",
    "Signal",
    "Goal",
    "Opportunity",
    "OLDHAM",
    "OLDHAM_SERVICES",
    "OLDHAM_LOCAL_WORKFLOWS",
    "NationalWorkflow",
    "NATIONAL_WORKFLOWS",
    "get_national_workflow",
    "list_national_workflows",
    "GOALS",
    "get_goal",
    "list_goals",
    "process_planning_signal",
    "process_business_signal",
    "process_contract_signal",
    "signals_to_opportunities",
]
