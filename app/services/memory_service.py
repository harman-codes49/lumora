import json
import re

from app.ai.llm import generate_response
from app.ai.prompts import LUMORA_SYSTEM_PROMPT


# =========================================================
# MEMORY EXTRACTION
# =========================================================

MEMORY_EXTRACTION_PROMPT = """
You are Lumora's long-term memory extraction system.

Your job is to identify ONLY useful, stable, low-risk facts
that would genuinely help Lumora understand the user in
future conversations.

DO NOT save:

- temporary emotions
- today's mood
- temporary stress
- arguments
- sensitive personal information
- passwords
- OTPs
- financial information
- medical diagnoses
- crisis information
- self-harm information
- abuse details
- private secrets
- guesses about the user
- information about other people's private lives
- random facts that will not help future conversations

GOOD MEMORY EXAMPLES:

"I prefer studying at night."
"I am learning Java."
"I prefer simple explanations."
"I'm preparing for placements."
"I like working on AI projects."
"I prefer Hinglish responses."

BAD MEMORY EXAMPLES:

"I'm stressed today."
"I had an argument with my friend."
"I feel terrible right now."
"My password is..."
"I want to die."
"I have a disease."

Return ONLY valid JSON.

If there is a useful memory, return:

{
    "should_save": true,
    "title": "Short memory title",
    "content": "Clear statement about the user",
    "category": "preference"
}

Allowed categories:

preference
habit
goal
learning
project
communication
general

If there is no useful memory, return:

{
    "should_save": false
}

Do not include markdown.
Do not include explanations.
"""


def clean_json_response(text):
    """
    Remove accidental markdown code fences.
    """

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def extract_memory(user_message):
    """
    Ask Gemini whether the user's message contains
    a useful long-term memory.
    """

    if not user_message:
        return None

    prompt = f"""
{MEMORY_EXTRACTION_PROMPT}

USER MESSAGE:

{user_message}
"""

    try:

        response = generate_response(
            user_message,
            LUMORA_SYSTEM_PROMPT + "\n\n" + prompt
        )

        cleaned = clean_json_response(response)

        data = json.loads(cleaned)

        if not isinstance(data, dict):
            return None

        if not data.get("should_save", False):
            return None

        title = str(
            data.get("title", "")
        ).strip()

        content = str(
            data.get("content", "")
        ).strip()

        category = str(
            data.get("category", "general")
        ).strip().lower()

        if not title or not content:
            return None

        allowed_categories = {
            "preference",
            "habit",
            "goal",
            "learning",
            "project",
            "communication",
            "general"
        }

        if category not in allowed_categories:
            category = "general"

        return {
            "title": title,
            "content": content,
            "category": category
        }

    except Exception as e:

        print(
            f"Lumora memory extraction error: {e}"
        )

        return None