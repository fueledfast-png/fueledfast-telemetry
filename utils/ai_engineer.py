import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are a senior race engineer with 15+ years experience in:
- GT3 / GT4
- Formula racing
- Professional sim racing (iRacing, ACC)

Your tone is:
- Technical
- Precise
- Instruction-focused
- No motivation, no hype

You speak like an engineer reviewing data in a debrief.
"""


def generate_ai_report(
    lap_summary: dict,
    sector_table: str,
    corner_table: str
) -> str:

    user_prompt = f"""
Analyze the following telemetry comparison.

LAP SUMMARY:
{lap_summary}

SECTOR DELTAS:
{sector_table}

CORNER ANALYSIS:
{corner_table}

Return feedback in EXACTLY this structure:

1. Overall Lap Time Analysis
2. Sector Performance Review
3. Braking & Entry Technique
4. Minimum Speed & Mid-Corner
5. Exit & Throttle Application
6. Top 5 Actionable Coaching Points
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
