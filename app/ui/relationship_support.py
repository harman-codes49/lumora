import streamlit as st

from app.ai.llm import generate_response
from app.ai.prompts import LUMORA_SYSTEM_PROMPT
from app.ai.safety import check_safety


# =========================================================
# RELATIONSHIP SUPPORT PROMPT
# =========================================================

RELATIONSHIP_PROMPT = """
You are Lumora's Relationship Support assistant.

Help the user think clearly about relationship situations
involving friends, partners, family, classmates, coworkers,
or other people.

IMPORTANT RULES:

- Do not automatically take the user's side.
- Do not automatically blame the other person.
- Separate facts from assumptions.
- Never claim to know another person's intentions or feelings.
- Consider multiple reasonable perspectives.
- Focus on communication, boundaries, expectations,
  misunderstandings and observable behavior.
- Do not encourage revenge, humiliation, stalking,
  manipulation, threats, coercion or harassment.
- Respect the user's autonomy.
- Give options rather than commands.
- Do not diagnose anyone.
- If there is immediate danger, abuse, coercion or serious
  safety risk, prioritize safety.

LANGUAGE:

Match the user's language.

If the user writes in Hinglish, respond naturally in Hinglish.
If the user writes in Hindi, respond naturally in Hindi.
If the user writes in English, respond naturally in English.

RESPONSE LENGTH:

Keep the response SHORT.

Do NOT write a huge paragraph.

Use exactly these sections:

### What I understand
2–3 short bullet points.

### What may be happening
2–3 short bullet points.

### What you can consider
3 short practical bullet points.

### If you want to say something
Give ONE short example message.

### Small next step
Give ONE simple next step.

Keep the entire response under 300 words.

Do not repeat the user's complete story.
Do not give a generic motivational speech.
"""


# =========================================================
# GENERATE GUIDANCE
# =========================================================

def generate_relationship_guidance(
    situation,
    goal,
    context=""
):

    safety_result = check_safety(situation)

    if safety_result["level"] == "high_risk":

        return safety_result["message"]

    safety_context = ""

    if safety_result["level"] == "caution":

        safety_context = f"""

SAFETY CONTEXT:

{safety_result["message"]}
"""

    prompt = f"""
{RELATIONSHIP_PROMPT}

USER'S SITUATION:

{situation}

USER'S GOAL:

{goal}

ADDITIONAL CONTEXT:

{context if context else "No additional context provided."}

{safety_context}

Now provide concise relationship guidance.
"""

    try:

        response = generate_response(
            situation,
            LUMORA_SYSTEM_PROMPT
            + "\n\n"
            + prompt
        )

        return response.strip()

    except Exception as e:

        print(
            f"Lumora relationship support error: {e}"
        )

        return (
            "I'm having trouble generating this guidance "
            "right now. Please try again in a moment."
        )


# =========================================================
# UI
# =========================================================

def render_relationship_support():

    # -----------------------------------------------------
    # DRAFT VALUES
    # -----------------------------------------------------

    situation_value = st.session_state.get(
        "relationship_draft_situation",
        ""
    )

    goal_value = st.session_state.get(
        "relationship_draft_goal",
        "General understanding"
    )

    context_value = st.session_state.get(
        "relationship_draft_context",
        ""
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.html("""
    <div style="
        margin-bottom: 24px;
    ">

        <div style="
            font-family: Georgia, serif;
            font-size: 32px;
            color: #30234f;
            margin-bottom: 6px;
        ">
            Relationship Support ♡
        </div>

        <div style="
            font-size: 14px;
            color: #817493;
        ">
            A calm space to think through communication,
            boundaries and difficult situations.
        </div>

    </div>
    """)

    # -----------------------------------------------------
    # INTRO
    # -----------------------------------------------------

    st.html("""
    <div style="
        background: #f3e8f7;
        border: 1px solid #eadcf0;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 20px;
        color: #5d4d70;
        font-size: 14px;
        line-height: 1.6;
    ">
        Lumora won't automatically take sides.
        It will help you look at the situation from
        different perspectives and think about what
        you can do next.
    </div>
    """)

    # -----------------------------------------------------
    # SITUATION
    # -----------------------------------------------------

    situation = st.text_area(
        "What's happening?",
        value=situation_value,
        placeholder=(
            "Tell Lumora what happened and what is "
            "bothering you..."
        ),
        height=130
    )

    # -----------------------------------------------------
    # GOAL
    # -----------------------------------------------------

    goal_options = [
        "General understanding",
        "How should I respond?",
        "How can I communicate this?",
        "How can I set a boundary?",
        "I want to understand both perspectives",
        "I'm unsure what to do next"
    ]

    goal_index = (
        goal_options.index(goal_value)
        if goal_value in goal_options
        else 0
    )

    goal = st.selectbox(
        "What would you like help with?",
        goal_options,
        index=goal_index
    )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = st.text_area(
        "Anything else Lumora should know? (optional)",
        value=context_value,
        placeholder="Add only the context that feels useful.",
        height=90
    )

    # -----------------------------------------------------
    # QUICK STARTING POINTS
    # -----------------------------------------------------

    st.html("""
    <div style="
        font-size: 14px;
        font-weight: 600;
        color: #4c3c62;
        margin-top: 8px;
        margin-bottom: 8px;
    ">
        Quick starting points
    </div>
    """)

    col1, col2, col3 = st.columns(3)

    with col1:

        communication_clicked = st.button(
            "💬 Communication",
            key="relationship_quick_communication",
            use_container_width=True
        )

    with col2:

        boundaries_clicked = st.button(
            "🌱 Boundaries",
            key="relationship_quick_boundaries",
            use_container_width=True
        )

    with col3:

        mixed_signals_clicked = st.button(
            "💭 Mixed Signals",
            key="relationship_quick_mixed_signals",
            use_container_width=True
        )

    # -----------------------------------------------------
    # QUICK BUTTON ACTIONS
    # -----------------------------------------------------

    if communication_clicked:

        st.session_state.relationship_draft_situation = (
            "I am having difficulty communicating "
            "something important to someone."
        )

        st.session_state.relationship_draft_goal = (
            "How can I communicate this?"
        )

        st.session_state.relationship_draft_context = ""

        st.rerun()

    if boundaries_clicked:

        st.session_state.relationship_draft_situation = (
            "I feel like I need to set a boundary "
            "in a relationship, but I am not sure "
            "how to communicate it."
        )

        st.session_state.relationship_draft_goal = (
            "How can I set a boundary?"
        )

        st.session_state.relationship_draft_context = ""

        st.rerun()

    if mixed_signals_clicked:

        st.session_state.relationship_draft_situation = (
            "Someone's behavior has been giving "
            "me mixed signals and I am unsure "
            "how to understand the situation."
        )

        st.session_state.relationship_draft_goal = (
            "I want to understand both perspectives"
        )

        st.session_state.relationship_draft_context = ""

        st.rerun()

    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    if st.button(
        "Get Lumora's perspective →",
        key="relationship_generate",
        use_container_width=True
    ):

        situation = situation.strip()
        context = context.strip()

        if not situation:

            st.warning(
                "Tell Lumora what's happening first."
            )

        else:

            # Save latest values as drafts
            st.session_state.relationship_draft_situation = (
                situation
            )

            st.session_state.relationship_draft_goal = (
                goal
            )

            st.session_state.relationship_draft_context = (
                context
            )

            with st.spinner(
                "Lumora is thinking..."
            ):

                response = generate_relationship_guidance(
                    situation=situation,
                    goal=goal,
                    context=context
                )

            st.session_state.relationship_response = (
                response
            )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    if "relationship_response" in st.session_state:

        st.html("""
        <div style="
            margin-top: 24px;
            padding: 12px 16px;
            border-radius: 12px;
            background: #f3e8f7;
            color: #6b587d;
            font-size: 11px;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        ">
            Lumora's perspective
        </div>
        """)

        st.markdown(
            st.session_state.relationship_response
        )

        if st.button(
            "Clear this guidance",
            key="clear_relationship_guidance"
        ):

            del st.session_state.relationship_response

            st.rerun()