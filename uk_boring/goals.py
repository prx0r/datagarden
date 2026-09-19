"""Goal definitions — what people actually want to accomplish.

Each Goal maps to workflows, expected outcomes, and data requirements.
The Goal tells UKGraph what to grow.
"""

from uk_boring.ontology import Goal


GOALS = {
    # UKBORING goals
    "move_home": Goal(
        goal_id="move_home",
        name="Move Home",
        description="Update all government and service records when moving house",
        category="property",
        place_required=True,
        workflows=["move_home"],
        expected_outcomes=["all_notifications_accepted", "new_addresses_registered"],
        typical_duration="2-4 weeks",
        recurring=False,
    ),
    "deal_with_letter": Goal(
        goal_id="deal_with_letter",
        name="Deal With Letter",
        description="Handle government correspondence",
        category="legal",
        place_required=False,
        workflows=["letter_workflow"],
        expected_outcomes=["obligation_resolved", "response_acknowledged"],
        typical_duration="1-7 days",
        recurring=True,
    ),
    "fix_home_problem": Goal(
        goal_id="fix_home_problem",
        name="Fix Home Problem",
        description="Find and book a tradesperson",
        category="property",
        place_required=True,
        workflows=["find_provider", "book_service"],
        expected_outcomes=["provider_booked", "work_completed"],
        typical_duration="1-2 weeks",
        recurring=False,
    ),

    # UKOPPORTUNITY goals
    "find_local_work": Goal(
        goal_id="find_local_work",
        name="Find Local Work",
        description="Find tenders, contracts, and business opportunities",
        category="business",
        place_required=True,
        workflows=["search_contracts", "match_capabilities"],
        expected_outcomes=["qualified_opportunities_found"],
        typical_duration="ongoing",
        recurring=True,
    ),
    "what_changed": Goal(
        goal_id="what_changed",
        name="What Changed",
        description="What changed in my area that affects my business?",
        category="business",
        place_required=True,
        workflows=["monitor_changes"],
        expected_outcomes=["changes_surfaced"],
        typical_duration="ongoing",
        recurring=True,
    ),

    # UKPRODUCTS goals
    "sell_item": Goal(
        goal_id="sell_item",
        name="Sell Item",
        description="Get the best price for a physical item",
        category="personal",
        place_required=False,
        workflows=["value_item", "list_item"],
        expected_outcomes=["item_sold", "optimal_price_achieved"],
        typical_duration="1-14 days",
        recurring=False,
    ),
    "buy_item": Goal(
        goal_id="buy_item",
        name="Buy Item",
        description="Find and purchase an item at fair value",
        category="personal",
        place_required=False,
        workflows=["value_item", "find_source", "verify_condition"],
        expected_outcomes=["item_purchased", "fair_price_paid"],
        typical_duration="1-7 days",
        recurring=False,
    ),
}


def get_goal(goal_id: str) -> Goal | None:
    """Look up a goal by ID."""
    return GOALS.get(goal_id)


def list_goals(outlet: str = None) -> list[Goal]:
    """List goals, optionally filtered by outlet."""
    goals = list(GOALS.values())
    if outlet:
        goals = [g for g in goals if _outlet_for_goal(g.goal_id) == outlet]
    return goals


def _outlet_for_goal(goal_id: str) -> str:
    """Map goal to its outlet."""
    outlet_map = {
        "move_home": "ukboring",
        "deal_with_letter": "ukboring",
        "fix_home_problem": "ukboring",
        "find_local_work": "ukopportunity",
        "what_changed": "ukopportunity",
        "sell_item": "ukproducts",
        "buy_item": "ukproducts",
    }
    return outlet_map.get(goal_id, "ukboring")
