"""Enumerations for FitBuddy Agent."""

from enum import Enum


class SectionStatus(str, Enum):
    """Status of a FitBuddy section."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class RouterDirective(str, Enum):
    """Router directive for navigation control."""
    STAY = "stay"
    NEXT = "next"
    MODIFY = "modify"


class SectionID(str, Enum):
    """FitBuddy section identifiers."""
    DIET_HABITS = "diet_habits"
    EXERCISE_HABITS = "exercise_habits"
    BODY_METRICS = "body_metrics"
    ADVICE = "advice"
