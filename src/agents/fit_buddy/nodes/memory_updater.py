"""Memory updater node for FitBuddy Agent."""

import logging

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from ..enums import RouterDirective, SectionID, SectionStatus
from ..models import SectionContent, SectionState, FitBuddyState

logger = logging.getLogger(__name__)


async def memory_updater_node(state: FitBuddyState, config: RunnableConfig) -> FitBuddyState:
    """
    Memory updater node that persists section states.

    Responsibilities:
    - Update section_states with latest content
    - Update user_data with extracted values
    - Manage short_memory size
    - Generate final advice when all sections are complete
    """
    current_section = state.get("current_section")
    logger.info(
        f"Memory updater node - Section: {current_section.value if current_section else 'unknown'}"
    )

    agent_out = state.get("agent_output")

    if not agent_out:
        logger.debug("No agent output to process")
        return state

    def _status_from_output(is_satisfied, directive):
        """Return status string."""
        if directive == RouterDirective.NEXT:
            return SectionStatus.DONE.value
        if is_satisfied is not None and is_satisfied:
            return SectionStatus.DONE.value
        return SectionStatus.IN_PROGRESS.value

    if agent_out.should_save_content:
        current_section_id = current_section.value if current_section else "unknown"

        messages = state.get("messages", [])
        last_ai_msg = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai_msg = msg
                break

        if last_ai_msg:
            plain_text = last_ai_msg.content

            section_content = SectionContent(
                content={"text": plain_text},
                plain_text=plain_text,
            )

            section_states = state.get("section_states", {})
            section_state = SectionState(
                section_id=current_section,
                content=section_content,
                satisfaction_status="satisfied" if agent_out.is_satisfied else None,
                status=SectionStatus(
                    _status_from_output(
                        agent_out.is_satisfied,
                        RouterDirective(agent_out.router_directive),
                    )
                ),
            )

            section_states[current_section_id] = section_state
            state["section_states"] = section_states

            logger.info(
                f"Updated section state for {current_section_id} "
                f"with status {section_state.status.value}"
            )

    section_states = state.get("section_states", {})
    all_sections = [
        SectionID.DIET_HABITS,
        SectionID.EXERCISE_HABITS,
        SectionID.BODY_METRICS,
    ]

    all_complete = all(
        section_id.value in section_states
        and section_states[section_id.value].status == SectionStatus.DONE
        for section_id in all_sections
    )

    current_section = state.get("current_section")
    is_last_collection_section = (
        current_section == SectionID.BODY_METRICS if current_section else False
    )

    user_done = False
    messages = state.get("messages", [])
    if messages:
        last_user_msg = None
        for msg in reversed(messages):
            from langchain_core.messages import HumanMessage

            if isinstance(msg, HumanMessage):
                last_user_msg = msg.content.lower() if hasattr(msg, "content") else ""
                break

        done_keywords = [
            "satisfied",
            "done",
            "finished",
            "complete",
            "good",
            "right",
            "proceed",
            "yes",
            "that's good",
            "that is good",
            "sounds good",
            "looks good",
        ]
        user_done = any(keyword in str(last_user_msg) for keyword in done_keywords) if last_user_msg else False

    if all_complete and is_last_collection_section and user_done:
        logger.info("[MEMORY_UPDATER] All data collection sections complete, moving to advice")
        state["should_generate_final_output"] = True
    elif all_complete:
        logger.info("[MEMORY_UPDATER] All collection sections marked as complete")

    short_memory = state.get("short_memory", [])
    if len(short_memory) > 20:
        short_memory = short_memory[-15:]
    state["short_memory"] = short_memory

    logger.debug(f"[MEMORY_UPDATER] short_memory length: {len(short_memory)}")

    return state
