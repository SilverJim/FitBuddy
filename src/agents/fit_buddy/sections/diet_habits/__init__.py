"""Diet habits section template."""

from ...enums import SectionID
from ..base_prompt import SectionTemplate

DIET_HABITS_TEMPLATE = SectionTemplate(
    section_id=SectionID.DIET_HABITS,
    name="Diet Habits",
    description="Collect information about the user's eating habits and dietary preferences.",
    system_prompt_template="""You are now in the Diet Habits section. Your goal is to understand the user's current eating patterns.

Ask the user about the following, ONE AT A TIME:
1. What does a typical day of eating look like for them? (breakfast, lunch, dinner, snacks)
2. Do they have any dietary preferences? (e.g., vegetarian, vegan, keto, paleo, no preference)
3. Are there any foods they avoid or are allergic to?
4. How much water do they typically drink per day?
5. Do they have any specific snacking habits? (e.g., healthy snacks, junk food, no snacks)

Guidelines:
- Start by asking about their typical daily meals
- Follow up naturally based on their responses
- Be supportive and non-judgmental about their current habits
- Once you have gathered information about all areas, present a summary and ask if they're satisfied
- Keep the conversation friendly and conversational
""",
    required_fields=["daily_meals", "dietary_preferences"],
    next_section=SectionID.EXERCISE_HABITS,
)
