"""Implementation node — generates personalized fitness advice."""

import logging

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from core.llm import get_model

from ..models import FitBuddyState

logger = logging.getLogger(__name__)


async def implementation_node(state: FitBuddyState, config: RunnableConfig) -> FitBuddyState:
    """Generate personalized diet and exercise advice based on collected data."""
    logger.info("Implementation node - generating personalized advice")

    user_data = state.get("user_data", {})
    section_states = state.get("section_states", {})

    llm = get_model()

    diet_content = ""
    exercise_content = ""
    body_metrics_content = ""

    diet_state = section_states.get("diet_habits")
    if diet_state and diet_state.content:
        diet_content = diet_state.content.plain_text or ""

    exercise_state = section_states.get("exercise_habits")
    if exercise_state and exercise_state.content:
        exercise_content = exercise_state.content.plain_text or ""

    body_state = section_states.get("body_metrics")
    if body_state and body_state.content:
        body_metrics_content = body_state.content.plain_text or ""

    user_data_dict = user_data.model_dump() if user_data else {}

    advice_prompt = (
        "You are FitBuddy, a professional fitness consultant. Based on the collected user data, "
        "generate comprehensive, personalized diet and exercise recommendations.\n\n"
        "COLLECTED DATA:\n"
        f"Diet Habits Summary:\n{diet_content}\n\n"
        f"Exercise Habits Summary:\n{exercise_content}\n\n"
        f"Body Metrics Summary:\n{body_metrics_content}\n\n"
        f"User Data Details: {user_data_dict}\n\n"
        "Please provide detailed, actionable advice in the following format:\n\n"
        "# Your Personalized Fitness Plan\n\n"
        "## Diet Recommendations\n"
        "[Specific meal timing, food choices, hydration, and snack advice]\n\n"
        "## Exercise Recommendations\n"
        "[Specific exercise schedule, types, duration, intensity, and progression advice]\n\n"
        "## Summary\n"
        "[Brief encouraging summary of the key points]\n\n"
        "Make the advice specific, actionable, and tailored to the user's profile. "
        "Use a supportive and encouraging tone."
    )

    messages = [SystemMessage(content=advice_prompt)]

    response = await llm.ainvoke(messages)

    advice_content = response.content if hasattr(response, "content") else str(response)

    state["final_advice"] = advice_content

    ai_message = AIMessage(
        content=(
            "Great news! I've put together your personalized fitness plan based on everything "
            "we've discussed. Here it is:\n\n"
            f"{advice_content}"
        )
    )

    state["messages"].append(ai_message)

    state["finished"] = True
    state["awaiting_user_input"] = False

    logger.info("Implementation node - advice generated successfully")

    return state
