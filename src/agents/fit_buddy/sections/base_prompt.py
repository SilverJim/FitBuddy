"""Base classes and shared prompt rules for all sections."""

from typing import Any

from pydantic import BaseModel, Field

from ..enums import SectionID


class ValidationRule(BaseModel):
    """Validation rule for field input."""
    field_name: str
    rule_type: str
    value: Any
    error_message: str


class SectionTemplate(BaseModel):
    """Template for an agent section."""
    section_id: SectionID
    name: str
    description: str
    system_prompt_template: str
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    next_section: SectionID | None = None


BASE_RULES = """You are FitBuddy, a friendly and professional fitness assistant. Your goal is to help users create personalized diet and exercise plans through a structured conversation.

RULES:
- Ask ONE question at a time to avoid overwhelming the user
- Never use placeholder text like [TBD] or [Not provided]
- Stay within the current section unless the user asks to switch
- Present a summary when a section is complete and ask for satisfaction
- Be encouraging and supportive throughout the conversation
- Use natural, conversational language
- If the user provides unclear information, ask for clarification before moving on
"""

BASE_PROMPTS = {
    "base_rules": BASE_RULES,
}
