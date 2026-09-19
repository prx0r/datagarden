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
)
from uk_boring.oldham import OLDHAM, OLDHAM_SERVICES

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
    "OLDHAM",
    "OLDHAM_SERVICES",
]
