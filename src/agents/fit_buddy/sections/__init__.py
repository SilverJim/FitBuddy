"""Section definitions for the FitBuddy agent."""

from .base_prompt import BASE_PROMPTS, BASE_RULES
from .diet_habits import DIET_HABITS_TEMPLATE
from .exercise_habits import EXERCISE_HABITS_TEMPLATE
from .body_metrics import BODY_METRICS_TEMPLATE
from .advice import ADVICE_TEMPLATE

SECTION_TEMPLATES = {
    "diet_habits": DIET_HABITS_TEMPLATE,
    "exercise_habits": EXERCISE_HABITS_TEMPLATE,
    "body_metrics": BODY_METRICS_TEMPLATE,
    "advice": ADVICE_TEMPLATE,
}

__all__ = [
    "BASE_RULES",
    "BASE_PROMPTS",
    "DIET_HABITS_TEMPLATE",
    "EXERCISE_HABITS_TEMPLATE",
    "BODY_METRICS_TEMPLATE",
    "ADVICE_TEMPLATE",
    "SECTION_TEMPLATES",
]
