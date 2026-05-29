"""Generate decision node for FitBuddy Agent."""

import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from ..enums import RouterDirective, SectionID, SectionStatus
from ..models import ChatAgentDecision, ChatAgentOutput, FitBuddyState

logger = logging.getLogger(__name__)


async def generate_decision_node(state: FitBuddyState, config: RunnableConfig) -> FitBuddyState:
    """
    Decision generation node that analyzes conversation and produces structured decisions.

    Responsibilities:
    - Analyze complete conversation including the just-generated reply
    - Generate structured decision data (router_directive, score, etc.)
    - Update state with agent_output containing complete ChatAgentOutput
    - Set router_directive and other state flags
    """
    context_packet = state.get("context_packet")
    if context_packet and hasattr(context_packet, "section_id"):
        current_section = context_packet.section_id
        logger.info(f"Generate decision node - Section: {current_section}")
    else:
        current_section = state["current_section"]
        logger.info(f"Generate decision node - Section: {current_section} (fallback)")

    messages = state.get("messages", [])
    if not messages or not isinstance(messages[-1], AIMessage):
        logger.error("DECISION_NODE: No AI reply found to analyze")
        default_decision = ChatAgentDecision(
            router_directive="stay",
            user_satisfaction_feedback=None,
            is_satisfied=None,
            should_save_content=False,
        )
        state["agent_output"] = ChatAgentOutput(
            reply="",
            **default_decision.model_dump(),
        )
        state["router_directive"] = "stay"
        return state

    last_ai_reply = messages[-1].content

    user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    last_user_msg = user_messages[-1].content.lower() if user_messages else ""

    is_last_section = (
        current_section == SectionID.ADVICE
        if hasattr(current_section, "value")
        else str(current_section) == "advice"
    )

    satisfaction_words = [
        "yes",
        "good",
        "great",
        "perfect",
        "continue",
        "next",
        "satisfied",
        "looks good",
        "right",
        "proceed",
        "done",
        "finished",
        "complete",
        "that's good",
        "that is good",
        "sounds good",
    ]
    is_satisfied = any(word in last_user_msg for word in satisfaction_words) if last_user_msg else None

    completion_words = [
        "satisfied",
        "done",
        "finished",
        "complete",
        "good",
        "right",
        "yes",
        "that's good",
        "that is good",
        "sounds good",
        "looks good",
    ]
    is_completion_signal = any(word in last_user_msg for word in completion_words) if last_user_msg else False

    summary_indicators = [
        "summary",
        "summarize",
        "let's summarize",
        "here's what",
        "here is what",
        "does this capture",
        "does this feel right",
        "anything you'd like to adjust",
        "anything you'd like to change",
        "satisfied",
        "accurate",
    ]
    agent_presented_summary = any(
        indicator in last_ai_reply.lower() for indicator in summary_indicators
    )

    current_section_id = (
        current_section.value if hasattr(current_section, "value") else str(current_section)
    )
    section_states = state.get("section_states", {})
    current_section_state = section_states.get(current_section_id) if section_states else None
    current_section_done = (
        current_section_state is not None
        and hasattr(current_section_state, "status")
        and current_section_state.status == SectionStatus.DONE
    )

    if state.get("final_advice"):
        router_directive = RouterDirective.STAY
        logger.info("Final advice already generated - allowing conversation to continue")
    elif is_last_section and is_completion_signal:
        router_directive = RouterDirective.STAY
    elif is_satisfied and (agent_presented_summary or current_section_done):
        router_directive = RouterDirective.NEXT
        logger.info(
            f"Moving to next section: summary_presented={agent_presented_summary}, "
            f"section_done={current_section_done}"
        )
    elif is_satisfied and not agent_presented_summary and not current_section_done:
        router_directive = RouterDirective.STAY
        logger.info("User satisfied but no summary yet - staying to allow Agent to summarize")
    else:
        router_directive = RouterDirective.STAY

    should_save_content = is_satisfied is True or "summary" in last_ai_reply.lower()

    decision = ChatAgentDecision(
        router_directive=router_directive.value,
        user_satisfaction_feedback=last_user_msg if last_user_msg else None,
        is_satisfied=is_satisfied,
        should_save_content=should_save_content,
    )

    state["agent_output"] = ChatAgentOutput(
        reply=last_ai_reply,
        **decision.model_dump(),
    )

    state["router_directive"] = router_directive.value

    logger.info(
        f"Decision: directive={router_directive.value}, satisfied={is_satisfied}, "
        f"last_section={is_last_section}"
    )

    return state
