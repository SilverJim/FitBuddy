"""Section prompts and navigation helpers for FitBuddy."""

from .enums import SectionID
from .sections import BASE_RULES, SECTION_TEMPLATES
from .sections.base_prompt import SectionTemplate


def get_section_template(section_id: SectionID) -> SectionTemplate:
    """Return the template for a given section."""
    template = SECTION_TEMPLATES.get(section_id.value)
    if not template:
        raise ValueError(f"Unknown section ID: {section_id}")
    return template


def get_next_section(current: SectionID) -> SectionID | None:
    """Return the next section in sequence, or None if all complete."""
    section_order = [
        SectionID.DIET_HABITS,
        SectionID.EXERCISE_HABITS,
        SectionID.BODY_METRICS,
        SectionID.ADVICE,
    ]
    try:
        current_index = section_order.index(current)
        if current_index < len(section_order) - 1:
            return section_order[current_index + 1]
    except ValueError:
        pass
    return None


def get_next_unfinished_section(section_states: dict) -> SectionID | None:
    """Find the first section that isn't done yet."""
    section_order = [
        SectionID.DIET_HABITS,
        SectionID.EXERCISE_HABITS,
        SectionID.BODY_METRICS,
        SectionID.ADVICE,
    ]
    for section_id in section_order:
        state = section_states.get(section_id.value)
        if not state or state.status != "done":
            return section_id
    return None


__all__ = [
    "BASE_RULES",
    "SECTION_TEMPLATES",
    "get_section_template",
    "get_next_section",
    "get_next_unfinished_section",
]
