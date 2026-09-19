"""The fundamental object: a Place.

A Place is the resolved subgraph around a location.
Everything in UK Boring decomposes into places, services, rules, and workflows.

Place hierarchy:
  UK → England → Greater Manchester → Oldham → ward → street → UPRN

Overlapping graphs:
  UPRN → administrative, electoral, health, utilities, transport, commercial
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Place:
    """A resolved location with all its jurisdictional context.

    Every physical address enters a "room" — a Place that knows
    which universe of rules applies.
    """
    # Identity
    uprn: str = ""                    # Unique Property Reference Number (strongest ID)
    postcode: str = ""                # Postcode
    address: str = ""                 # Full address

    # Administrative hierarchy
    country: str = ""                 # England, Scotland, Wales, NI
    region: str = ""                  # e.g. "North West"
    county: str = ""                  # e.g. "Greater Manchester"
    district: str = ""                # e.g. "Oldham"
    ward: str = ""                    # e.g. "Failsworth West"

    # Jurisdiction overlays
    local_authority: str = ""         # e.g. "Oldham Metropolitan Borough Council"
    la_gss_code: str = ""             # e.g. "E08000004"
    constituency: str = ""            # Parliamentary constituency
    police_force: str = ""            # e.g. "Greater Manchester Police"
    nhs_board: str = ""               # e.g. "NHS Oldham CCG"
    water_company: str = ""           # e.g. "United Utilities"
    waste_authority: str = ""         # Usually same as LA
    planning_authority: str = ""      # Usually same as LA
    transport_authority: str = ""     # e.g. "Transport for Greater Manchester"

    # Available services (resolved from LA + national)
    services: list = field(default_factory=list)  # list of service IDs

    # Available workflows
    workflows: list = field(default_factory=list)  # list of workflow IDs

    # Source
    source: str = ""                  # where this was resolved from
    resolved_at: str = ""             # ISO UTC

    def to_dict(self) -> dict:
        return self.__dict__.copy()
