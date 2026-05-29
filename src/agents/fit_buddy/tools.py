"""Tools for FitBuddy Agent."""

import logging
import re
from typing import Any

from langchain_core.tools import tool

from .enums import SectionID, SectionStatus
from .prompts import BASE_RULES, SECTION_TEMPLATES

logger = logging.getLogger(__name__)


@tool
async def get_context(
    user_id: int,
    thread_id: str,
    section_id: str,
    user_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Get context packet for a specific FitBuddy section.

    Fetches section data and generates the appropriate system prompt
    based on the section template.

    Args:
        user_id: Integer user ID
        thread_id: Thread identifier
        section_id: Section identifier
        user_data: Current user data for template rendering

    Returns:
        Context packet with system prompt and draft content
    """
    logger.info(f"Getting context for section: {section_id}, user: {user_id}, thread: {thread_id}")

    template = SECTION_TEMPLATES.get(section_id)
    if not template:
        raise ValueError(f"Unknown section ID: {section_id}")

    base_prompt = BASE_RULES
    section_prompt = template.system_prompt_template

    if user_data is None:
        user_data = {}

    def _replace_placeholder(match):
        key = match.group(1)
        return str(user_data.get(key, "")) if isinstance(user_data, dict) else ""

    section_prompt = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", _replace_placeholder, section_prompt)

    system_prompt = f"{base_prompt}\n\n---\n\n{section_prompt}"

    draft = None
    status = SectionStatus.PENDING.value

    try:
        SectionID(section_id)
    except ValueError:
        logger.error(f"Invalid section_id: {section_id}")
        raise ValueError(f"Unknown section ID: {section_id}")

    if status not in [s.value for s in SectionStatus]:
        logger.warning(f"Invalid status: {status}, defaulting to PENDING")
        status = SectionStatus.PENDING.value

    return {
        "section_id": section_id,
        "status": status,
        "system_prompt": system_prompt,
        "draft": draft,
        "validation_rules": {
            str(i): rule.model_dump()
            for i, rule in enumerate(getattr(template, "validation_rules", []))
        },
    }


__all__ = [
    "get_context",
]
