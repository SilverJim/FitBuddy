"""Advice section template."""

from ...enums import SectionID
from ..base_prompt import SectionTemplate

ADVICE_TEMPLATE = SectionTemplate(
    section_id=SectionID.ADVICE,
    name="Personalized Advice",
    description="Generate comprehensive diet and exercise recommendations based on collected data.",
    system_prompt_template="""You are now in the final Advice section. Based on all the information you've collected, generate comprehensive, personalized recommendations.

Review the collected data:
- Diet habits: daily meals, dietary preferences, food restrictions, water intake, snack habits
- Exercise habits: frequency, types, duration, intensity, fitness level
- Body metrics: weight, height, age, gender

Provide personalized recommendations in two main areas:

1. DIET RECOMMENDATIONS:
   - Suggest meal timing and structure based on their current habits
   - Recommend specific food choices aligned with their preferences and restrictions
   - Give hydration advice
   - Suggest improvements to snack habits if needed

2. EXERCISE RECOMMENDATIONS:
   - Suggest an exercise schedule based on their current frequency and goals
   - Recommend exercise types that complement their current routine
   - Advise on workout duration and intensity progression
   - Suggest exercises appropriate for their fitness level

Guidelines:
- Make recommendations specific and actionable
- Consider all collected data when forming advice
- Be realistic and gradual in suggestions
- Present the advice in a clear, organized format
""",
    required_fields=[],
    next_section=None,
)
