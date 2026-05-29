"""Routing logic for FitBuddy Agent graph."""

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage

from ..enums import RouterDirective
from ..models import FitBuddyState


def route_after_memory_updater(state: FitBuddyState) -> Literal["implementation", "router"]:
    """Route after memory_updater — generate final advice or loop back."""
    if state.get("should_generate_final_output", False):
        return "implementation"
    return "router"


def route_decision(state: FitBuddyState) -> Literal["generate_reply"] | None:
    """Determine whether to generate a reply or end the turn."""

    def has_pending_user_input() -> bool:
        msgs = state.get("messages", [])
        if not msgs:
            return False
        return isinstance(msgs[-1], HumanMessage)

    if state.get("finished", False):
        if has_pending_user_input():
            return "generate_reply"
        return None

    directive = state.get("router_directive")

    if directive == RouterDirective.STAY or (
        isinstance(directive, str) and directive.lower() == "stay"
    ):
        if has_pending_user_input():
            return "generate_reply"
        if state.get("awaiting_user_input", False):
            return None
        return None

    elif directive == RouterDirective.NEXT or (
        isinstance(directive, str) and directive.startswith("modify:")
    ):
        return "generate_reply"

    return None
