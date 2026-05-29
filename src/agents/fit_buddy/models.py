"""Pydantic models for FitBuddy Agent."""

import uuid
from typing import Any

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, field_validator

from .enums import RouterDirective, SectionID, SectionStatus
from .sections.base_prompt import SectionTemplate, ValidationRule


class SectionContent(BaseModel):
    """Content for a FitBuddy section."""
    content: dict[str, Any]
    plain_text: str | None = None


class SectionState(BaseModel):
    """State of a single section."""
    section_id: SectionID
    content: SectionContent | None = None
    satisfaction_status: str | None = None
    status: SectionStatus = SectionStatus.PENDING


class ContextPacket(BaseModel):
    """Context packet loaded by the router for the current section."""
    section_id: SectionID
    status: SectionStatus
    system_prompt: str
    draft: SectionContent | None = None
    validation_rules: dict[str, Any] | None = None


class FitBuddyData(BaseModel):
    """Domain-specific data collected from the user."""
    # Diet habits section
    daily_meals: list[str] = Field(default_factory=list)
    dietary_preferences: str | None = None
    food_restrictions: list[str] = Field(default_factory=list)
    water_intake: str | None = None
    snack_habits: str | None = None

    # Exercise habits section
    exercise_frequency: str | None = None
    exercise_types: list[str] = Field(default_factory=list)
    exercise_duration: str | None = None
    exercise_intensity: str | None = None
    fitness_level: str | None = None

    # Body metrics section
    weight: float | None = None
    height: float | None = None
    age: int | None = None
    gender: str | None = None
    bmi: float | None = None

    # Advice section
    diet_advice: str | None = None
    exercise_advice: str | None = None


class ChatAgentDecision(BaseModel):
    """Structured decision from the generate_decision node."""
    router_directive: str = Field(
        ...,
        description="Navigation control: 'stay', 'next', or 'modify:<section_id>'",
    )
    user_satisfaction_feedback: str | None = Field(
        None, description="User's feedback about satisfaction with the section."
    )
    is_satisfied: bool | None = Field(
        None, description="Whether the user is satisfied with the current section."
    )
    should_save_content: bool = Field(
        False,
        description="Whether to save the current section content.",
    )

    @field_validator("router_directive")
    def validate_router_directive(cls, v):
        if v not in ["stay", "next"] and not v.startswith("modify:"):
            raise ValueError("router_directive must be 'stay', 'next', or 'modify:<section_id>'")
        return v


class ChatAgentOutput(BaseModel):
    """Complete output from the generate_reply + generate_decision nodes."""
    reply: str = Field(..., description="Conversational response to the user.")
    router_directive: str = Field(
        ...,
        description="Navigation control: 'stay', 'next', or 'modify:<section_id>'",
    )
    user_satisfaction_feedback: str | None = None
    is_satisfied: bool | None = None
    should_save_content: bool = False

    @field_validator("router_directive")
    def validate_router_directive(cls, v):
        if v not in ["stay", "next"] and not v.startswith("modify:"):
            raise ValueError("router_directive must be 'stay', 'next', or 'modify:<section_id>'")
        return v


class FitBuddyState(MessagesState):
    """State for the FitBuddy agent."""
    user_id: int = 1
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    current_section: SectionID = SectionID.DIET_HABITS
    context_packet: ContextPacket | None = None
    section_states: dict[str, SectionState] = Field(default_factory=dict)
    router_directive: str = RouterDirective.NEXT
    finished: bool = False

    user_data: FitBuddyData = Field(default_factory=FitBuddyData)

    short_memory: list[BaseMessage] = Field(default_factory=list)

    agent_output: ChatAgentOutput | None = None
    awaiting_user_input: bool = False
    awaiting_satisfaction_feedback: bool = False

    error_count: int = 0
    last_error: str | None = None

    final_advice: str | None = None
    should_generate_final_output: bool = False
