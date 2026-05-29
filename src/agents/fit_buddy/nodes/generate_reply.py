"""Generate reply node for FitBuddy Agent."""

import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from core.llm import get_model

from ..enums import SectionStatus
from ..models import FitBuddyState

logger = logging.getLogger(__name__)


async def generate_reply_node(state: FitBuddyState, config: RunnableConfig) -> FitBuddyState:
    """
    Reply generation node that produces conversational responses.

    Responsibilities:
    - Generate conversational reply based on context_packet system prompt
    - Add reply to conversation history
    - Update short_memory
    """
    if state.get("finished", False) and state.get("messages"):
        last_msg = state["messages"][-1]
        if isinstance(last_msg, HumanMessage):
            logger.info("User sent message after advice generation - resetting finished flag")
            state["finished"] = False

    logger.info(
        f"Generate reply node - Section: {state['current_section']}, "
        f"finished={state.get('finished', False)}"
    )

    context_packet = state.get("context_packet")

    llm = get_model()

    messages: list[BaseMessage] = []

    if state.get("context_packet"):
        messages.append(SystemMessage(content=state["context_packet"].system_prompt))

        section_names = {
            "diet_habits": "Diet Habits",
            "exercise_habits": "Exercise Habits",
            "body_metrics": "Body Metrics",
            "advice": "Personalized Advice",
        }

        completed_sections = []
        for section_id, section_state in state.get("section_states", {}).items():
            if section_state.status == SectionStatus.DONE:
                section_name = section_names.get(section_id, section_id)
                completed_sections.append(section_name)

        current_section_name = section_names.get(
            state["current_section"].value, state["current_section"].value
        )

        progress_info = (
            f"\n\nSYSTEM STATUS:\n"
            f"- Total sections: 4\n"
            f"- Completed: {len(completed_sections)} sections"
        )
        if completed_sections:
            progress_info += f" ({', '.join(completed_sections)})"
        progress_info += f"\n- Currently working on: {current_section_name}\n"

        messages.append(SystemMessage(content=progress_info))

        current_section_id = state["current_section"].value
        section_state = state.get("section_states", {}).get(current_section_id)
        if not section_state or not section_state.content:
            new_section_instruction = (
                f"IMPORTANT: You are now in the {current_section_id} section. "
                "This is a NEW section with no content yet. "
                "Start by following the conversation flow defined in the section prompt. "
                "Do NOT reference or include content from previous sections."
            )
            messages.append(SystemMessage(content=new_section_instruction))

    messages.extend(state.get("short_memory", []))

    if state.get("messages"):
        _last_msg = state["messages"][-1]
        if isinstance(_last_msg, HumanMessage):
            messages.append(_last_msg)

    if state.get("final_advice"):
        final_advice_context = (
            "\n\nIMPORTANT CONTEXT: Personalized advice has already been generated for this conversation. "
            "The user may have additional questions or want to modify their profile. "
            "Be helpful and responsive to their requests."
        )
        messages.append(SystemMessage(content=final_advice_context))

    response = await llm.ainvoke(messages)

    reply_content = response.content if hasattr(response, "content") else str(response)

    ai_message = AIMessage(content=reply_content)

    state["messages"].append(ai_message)

    short_memory = state.get("short_memory", [])
    short_memory.append(ai_message)
    if len(short_memory) > 10:
        short_memory = short_memory[-10:]
    state["short_memory"] = short_memory

    state["awaiting_user_input"] = True

    logger.info(f"Generated reply for section {state['current_section'].value}")

    return state
