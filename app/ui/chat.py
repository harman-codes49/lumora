import html
import streamlit as st

from app.ai.llm import generate_response_stream
from app.ai.prompts import LUMORA_SYSTEM_PROMPT
from app.ai.safety import check_safety
from app.services.memory_service import extract_memory

from app.database.models import (
    save_long_term_memory,
    long_term_memory_exists,
    create_conversation,
    save_message,
    get_messages,
    save_important_date,
    get_conversations,
    update_conversation_title,
    delete_conversation,
)

from app.services.date_service import extract_important_dates


# =========================================================
# SESSION STATE
# =========================================================

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "pending_date_suggestions" not in st.session_state:
    st.session_state.pending_date_suggestions = []


# =========================================================
# CHAT CSS
# =========================================================

_CHAT_CSS = ("""
<style>

/* =====================================================
   CHAT HEADER
   ===================================================== */

.chat-header {
    padding: 10px 0 20px 0;
}

.chat-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    color: #403858;
}

.chat-subtitle {
    color: #8b8192;
    font-size: 13px;
    margin-top: 4px;
}


/* =====================================================
   CHAT ROWS
   ===================================================== */

.chat-row {
    display: flex;
    width: 100%;
    margin: 14px 0;
    gap: 10px;
    align-items: flex-start;
}


/* =====================================================
   USER MESSAGE
   ===================================================== */

.chat-row-user {
    justify-content: flex-end;
}

.user-avatar {
    width: 34px;
    height: 34px;
    min-width: 34px;

    border-radius: 50%;

    background: #e8def2;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 16px;

    margin-top: 2px;
}

.chat-message-user {
    background: #eee7f5;

    padding: 13px 16px;

    border-radius: 18px 18px 5px 18px;

    max-width: 72%;

    color: #403858;

    line-height: 1.6;

    box-shadow:
        0 2px 8px rgba(80, 65, 100, 0.04);
}


/* =====================================================
   LUMORA MESSAGE
   ===================================================== */

.chat-row-assistant {
    justify-content: flex-start;
}

.lumora-avatar {
    width: 34px;
    height: 34px;
    min-width: 34px;

    border-radius: 50%;

    background: #dcd0ea;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 16px;

    margin-top: 2px;
}

.chat-message-assistant {
    background: #ffffff;

    border: 1px solid #eee7f3;

    padding: 13px 16px;

    border-radius: 18px 18px 18px 5px;

    max-width: 72%;

    color: #403858;

    line-height: 1.6;

    box-shadow:
        0 3px 12px rgba(80, 65, 100, 0.05);
}


/* =====================================================
   CHAT NAMES
   ===================================================== */

.chat-role-user {
    font-size: 11px;
    font-weight: 600;

    color: #81728e;

    margin-bottom: 5px;

    text-align: right;
}

.chat-role-lumora {
    font-size: 11px;
    font-weight: 600;

    color: #8b7199;

    margin-bottom: 5px;
}


/* =====================================================
   STREAMING
   ===================================================== */

.streaming-message {
    min-height: 20px;
}


/* =====================================================
   TYPING INDICATOR
   ===================================================== */

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 7px;

    color: #8b7199;

    font-size: 13px;
}

.typing-dots {
    letter-spacing: 3px;
    animation: typingDots 1.2s infinite;
}

@keyframes typingDots {

    0% {
        opacity: 0.25;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.25;
    }
}


/* =====================================================
   DATE SUGGESTION
   ===================================================== */

.date-suggestion {
    background: #f7f0fa;

    border: 1px solid #e5d7ed;

    border-radius: 18px;

    padding: 16px;

    margin: 15px 0;
}

.date-suggestion-title {
    font-family: 'Playfair Display', serif;

    font-size: 18px;

    color: #403858;
}

.date-suggestion-text {
    color: #71677c;

    font-size: 13px;

    margin-top: 6px;

    line-height: 1.5;
}


/* =====================================================
   CONVERSATIONS
   ===================================================== */

.conversation-section {
    margin-top: 18px;
    margin-bottom: 8px;
}

</style>
""")


# =========================================================
# CREATE / GET CURRENT CONVERSATION
# =========================================================

def ensure_conversation():

    if st.session_state.current_conversation_id is None:

        conversation_id = create_conversation(
            title="New Conversation"
        )

        st.session_state.current_conversation_id = conversation_id

    return st.session_state.current_conversation_id


# =========================================================
# LOAD CURRENT MESSAGES
# =========================================================

def load_current_messages():

    conversation_id = (
        st.session_state.current_conversation_id
    )

    if conversation_id is None:
        return []

    return get_messages(conversation_id)


# =========================================================
# BUILD CONVERSATION CONTEXT
# =========================================================

def build_conversation_context(messages):

    if not messages:
        return ""

    recent_messages = messages[-12:]

    context_parts = []

    for message in recent_messages:

        role = message["role"]
        content = message["content"]

        if role == "user":

            context_parts.append(
                f"User: {content}"
            )

        elif role == "assistant":

            context_parts.append(
                f"Lumora: {content}"
            )

    return "\n".join(context_parts)


# =========================================================
# GENERATE AUTOMATIC CONVERSATION TITLE
# =========================================================

def generate_conversation_title(user_message):

    text = user_message.strip()

    if not text:
        return "New Conversation"

    punctuation = ".,!?;:()[]{}\"'"

    for character in punctuation:
        text = text.replace(character, "")

    words = text.split()

    if not words:
        return "New Conversation"

    title_words = words[:6]

    title = " ".join(title_words)

    if len(words) > 6:
        title += "..."

    return title.capitalize()


# =========================================================
# UPDATE TITLE FOR FIRST MESSAGE
# =========================================================

def update_title_if_first_message(
    conversation_id,
    user_message
):

    messages = get_messages(
        conversation_id
    )

    if len(messages) == 1:

        conversation_title = (
            generate_conversation_title(
                user_message
            )
        )

        update_conversation_title(
            conversation_id,
            conversation_title
        )


# =========================================================
# DATE CONFIRMATION UI
# =========================================================

def render_pending_date_suggestions():

    if not st.session_state.pending_date_suggestions:
        return

    st.html("""
    <div class="date-suggestion">

        <div class="date-suggestion-title">
            💜 Save an important date?
        </div>

        <div class="date-suggestion-text">
            Lumora noticed that you mentioned an important date.
            Would you like to save it to your Calendar and receive
            a reminder?
        </div>

    </div>
    """)

    remaining_suggestions = []

    for index, suggestion in enumerate(
        st.session_state.pending_date_suggestions
    ):

        title = suggestion.get(
            "title",
            "Important Date"
        )

        detected_date = suggestion.get(
            "date",
            ""
        )

        note = suggestion.get(
            "note",
            ""
        )

        safe_title = html.escape(
            str(title)
        )

        safe_date = html.escape(
            str(detected_date)
        )

        safe_note = html.escape(
            str(note)
        )

        st.markdown(
            f"📅 **{safe_title}** — `{safe_date}`"
        )

        if note:

            st.caption(
                safe_note
            )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💜 Save & Remind Me",
                key=f"save_date_{index}",
                use_container_width=True
            ):

                save_important_date(
                    title=str(title),
                    date=str(detected_date),
                    note=str(note),
                    reminder_enabled=True
                )

                st.success(
                    f"Saved **{safe_title}** to your important dates. 💜"
                )

                continue

        with col2:

            if st.button(
                "Not now",
                key=f"skip_date_{index}",
                use_container_width=True
            ):

                continue

        remaining_suggestions.append(
            suggestion
        )

    st.session_state.pending_date_suggestions = (
        remaining_suggestions
    )


# =========================================================
# NEW CHAT
# =========================================================

def start_new_chat():

    conversation_id = create_conversation(
        title="New Conversation"
    )

    st.session_state.current_conversation_id = (
        conversation_id
    )

    st.session_state.pending_date_suggestions = []

    st.rerun()


# =========================================================
# CONVERSATION SIDEBAR
# =========================================================

def render_conversation_list():

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 💬 Your Conversations"
    )


    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.sidebar.button(
        "＋ New Chat",
        key="new_chat_button",
        use_container_width=True
    ):

        start_new_chat()


    conversations = get_conversations()

    current_id = (
        st.session_state.current_conversation_id
    )


    if not conversations:

        st.sidebar.caption(
            "No conversations yet."
        )

        return


    for conversation in conversations:

        conversation_id = conversation["id"]

        title = conversation["title"]

        if not title:
            title = "New Conversation"

        display_title = str(title)[:30]

        if len(str(title)) > 30:
            display_title += "..."


        # -------------------------------------------------
        # CONVERSATION ROW
        # -------------------------------------------------

        col1, col2 = st.sidebar.columns(
            [5, 1]
        )

        with col1:

            if conversation_id == current_id:

                button_label = (
                    f"🟣 {display_title}"
                )

            else:

                button_label = (
                    f"💬 {display_title}"
                )

            if st.button(
                button_label,
                key=f"conversation_{conversation_id}",
                use_container_width=True
            ):

                st.session_state.current_conversation_id = (
                    conversation_id
                )

                st.session_state.pending_date_suggestions = []

                st.rerun()


        with col2:

            if st.button(
                "⋯",
                key=f"conversation_menu_{conversation_id}",
                help="Conversation options"
            ):

                menu_key = (
                    f"show_conversation_menu_{conversation_id}"
                )

                st.session_state[menu_key] = not st.session_state.get(
                    menu_key,
                    False
                )

                st.rerun()


        # -------------------------------------------------
        # CONVERSATION ACTIONS
        # -------------------------------------------------

        menu_key = (
            f"show_conversation_menu_{conversation_id}"
        )

        if st.session_state.get(menu_key, False):

            action_col1, action_col2 = (
                st.sidebar.columns(2)
            )

            with action_col1:

                if st.button(
                    "✏️ Rename",
                    key=f"rename_{conversation_id}",
                    use_container_width=True
                ):

                    st.session_state[
                        f"rename_conversation_{conversation_id}"
                    ] = True

                    st.rerun()


            with action_col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{conversation_id}",
                    use_container_width=True
                ):

                    delete_conversation(
                        conversation_id
                    )

                    if conversation_id == current_id:

                        st.session_state.current_conversation_id = None

                    st.session_state.pending_date_suggestions = []

                    st.session_state.pop(
                        f"show_conversation_menu_{conversation_id}",
                        None
                    )

                    st.session_state.pop(
                        f"rename_conversation_{conversation_id}",
                        None
                    )

                    st.rerun()


        # -------------------------------------------------
        # RENAME INPUT
        # -------------------------------------------------

        rename_key = (
            f"rename_conversation_{conversation_id}"
        )

        if st.session_state.get(rename_key, False):

            new_title = st.sidebar.text_input(
                "Conversation name",
                value=str(title),
                key=f"rename_input_{conversation_id}"
            )

            rename_col1, rename_col2 = (
                st.sidebar.columns(2)
            )

            with rename_col1:

                if st.button(
                    "Save",
                    key=f"save_rename_{conversation_id}",
                    use_container_width=True
                ):

                    new_title = new_title.strip()

                    if new_title:

                        update_conversation_title(
                            conversation_id,
                            new_title
                        )

                    st.session_state[rename_key] = False

                    st.session_state.pop(
                        f"show_conversation_menu_{conversation_id}",
                        None
                    )

                    st.rerun()


            with rename_col2:

                if st.button(
                    "Cancel",
                    key=f"cancel_rename_{conversation_id}",
                    use_container_width=True
                ):

                    st.session_state[rename_key] = False

                    st.session_state.pop(
                        f"show_conversation_menu_{conversation_id}",
                        None
                    )

                    st.rerun()


# =========================================================
# DISPLAY CHAT MESSAGE
# =========================================================

def render_message(message):

    role = message["role"]

    content = str(
        message["content"]
    )

    safe_content = html.escape(
        content
    ).replace(
        "\n",
        "<br>"
    )


    # =====================================================
    # USER MESSAGE
    # =====================================================

    if role == "user":

        st.html(
            f"""
            <div class="chat-row chat-row-user">

                <div class="chat-message-user">

                    <div class="chat-role-user">
                        You
                    </div>

                    <div>
                        {safe_content}
                    </div>

                </div>

                <div class="user-avatar">
                    👤
                </div>

            </div>
            """
        )


    # =====================================================
    # LUMORA MESSAGE
    # =====================================================

    elif role == "assistant":

        st.html(
            f"""
            <div class="chat-row chat-row-assistant">

                <div class="lumora-avatar">
                    🌿
                </div>

                <div class="chat-message-assistant">

                    <div class="chat-role-lumora">
                        Lumora
                    </div>

                    <div>
                        {safe_content}
                    </div>

                </div>

            </div>
            """
        )


# =========================================================
# RENDER CHAT PAGE
# =========================================================

def render_chat():
    st.html(_CHAT_CSS)


    # -----------------------------------------------------
    # MAKE SURE CONVERSATION EXISTS
    # -----------------------------------------------------

    ensure_conversation()


    # -----------------------------------------------------
    # SIDEBAR CONVERSATIONS
    # -----------------------------------------------------

    render_conversation_list()


    # -----------------------------------------------------
    # CHAT HEADER
    # -----------------------------------------------------

    st.html("""
    <div class="chat-header">

        <div class="chat-title">
            Talk to Lumora 💬
        </div>

        <div class="chat-subtitle">
            A safe space to talk, reflect and be heard.
        </div>

    </div>
    """)


    # -----------------------------------------------------
    # DATE CONFIRMATION
    # -----------------------------------------------------

    render_pending_date_suggestions()


    # -----------------------------------------------------
    # LOAD EXISTING MESSAGES
    # -----------------------------------------------------

    messages = load_current_messages()


    # -----------------------------------------------------
    # DISPLAY CONVERSATION HISTORY
    # -----------------------------------------------------

    for message in messages:

        render_message(
            message
        )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    user_message = st.chat_input(
        "Tell Lumora what's on your mind..."
    )

    if not user_message:
        return


    user_message = user_message.strip()

    if not user_message:
        return


    # =====================================================
    # CURRENT CONVERSATION
    # =====================================================

    conversation_id = ensure_conversation()


    # =====================================================
    # SAFETY CHECK
    # =====================================================

    safety_result = check_safety(
        user_message
    )


    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    save_message(
        conversation_id,
        "user",
        user_message
    )


    # =====================================================
    # ⭐ SHOW USER MESSAGE IMMEDIATELY
    # =====================================================

    render_message(
        {
            "role": "user",
            "content": user_message
        }
    )


    # =====================================================
    # ⭐ SHOW LUMORA TYPING INDICATOR
    # =====================================================

    typing_placeholder = st.empty()

    typing_placeholder.html(
        """
        <div class="chat-row chat-row-assistant">

            <div class="lumora-avatar">
                🌿
            </div>

            <div class="chat-message-assistant">

                <div class="chat-role-lumora">
                    Lumora
                </div>

                <div class="typing-indicator">
                    <span>Lumora is typing</span>
                    <span class="typing-dots">•••</span>
                </div>

            </div>

        </div>
        """
    )


    # =====================================================
    # AUTOMATIC CONVERSATION TITLE
    # =====================================================

    update_title_if_first_message(
        conversation_id,
        user_message
    )


    # =====================================================
    # DATE DETECTION
    #
    # This happens before Gemini so date confirmation
    # can still appear even if Gemini temporarily fails.
    # =====================================================

    detected_dates = []

    try:

        detected_dates = (
            extract_important_dates(
                user_message
            )
        )

    except Exception as e:

        print(
            f"Lumora date detection error: {e}"
        )


    # -----------------------------------------------------
    # STORE DATE SUGGESTIONS
    # -----------------------------------------------------

    if detected_dates:

        for detected_date in detected_dates:

            already_pending = any(

                existing["date"]
                == detected_date["date"]

                and

                existing["title"]
                == detected_date["title"]

                for existing
                in st.session_state.pending_date_suggestions
            )

            if not already_pending:

                st.session_state.pending_date_suggestions.append(
                    detected_date
                )


    # =====================================================
    # HIGH-RISK SAFETY RESPONSE
    # =====================================================

    if safety_result["level"] == "high_risk":

        # Remove typing indicator
        typing_placeholder.empty()

        response_text = (
            safety_result["message"]
        )

        save_message(
            conversation_id,
            "assistant",
            response_text
        )

        render_message(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        return


    # =====================================================
    # CAUTION RESPONSE
    # =====================================================

    if safety_result["level"] == "caution":

        safety_context = (
            safety_result["message"]
        )

    else:

        safety_context = ""


    # =====================================================
    # LOAD UPDATED CONVERSATION
    # =====================================================

    updated_messages = get_messages(
        conversation_id
    )


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    conversation_context = (
        build_conversation_context(
            updated_messages
        )
    )


    # =====================================================
    # LUMORA CONTEXT
    # =====================================================

    contextual_prompt = f"""

You are Lumora, a multilingual AI wellbeing companion.

Use the conversation history below to maintain continuity.

IMPORTANT INSTRUCTIONS:

- Remember relevant information already shared in this conversation.
- Do not repeatedly ask the user to explain something they already explained.
- Do not invent memories, facts, events or personal information.
- Match the user's language and style.
- If the user speaks in Hinglish, respond naturally in Hinglish.
- If the user speaks Hindi, respond naturally in Hindi.
- If the user speaks English, respond naturally in English.
- Be warm, calm, empathetic and practical.
- Do not diagnose mental-health conditions.
- Do not pretend to be a therapist, doctor or emergency service.
- Respect the user's autonomy.
- For relationship situations, do not automatically blame either person.
- Do not make unsupported assumptions about another person's intentions.
- If an important date is detected, do NOT claim that it has been saved.
- A date is saved only after the user explicitly clicks "Save & Remind Me".
- Do not tell the user that a reminder has been created unless they actually clicked the save button.

RECENT CONVERSATION:

{conversation_context}

CURRENT USER MESSAGE:

{user_message}

"""


    # =====================================================
    # ADD SAFETY CONTEXT IF REQUIRED
    # =====================================================

    if safety_context:

        contextual_prompt += f"""

SAFETY CONTEXT:

{safety_context}

"""


    # =====================================================
    # GENERATE LUMORA RESPONSE - STREAMING
    # =====================================================

    full_system_prompt = (
        LUMORA_SYSTEM_PROMPT
        + "\n\n"
        + contextual_prompt
    )


    # -----------------------------------------------------
    # RESPONSE PLACEHOLDER
    # -----------------------------------------------------

    response_placeholder = st.empty()

    response_text = ""


    # =====================================================
    # GEMINI RESPONSE
    # =====================================================

    try:

        first_chunk = True

        for chunk in generate_response_stream(
            user_message,
            full_system_prompt
        ):

            # -------------------------------------------------
            # ⭐ REMOVE "LUMORA IS TYPING" WHEN RESPONSE STARTS
            # -------------------------------------------------

            if first_chunk:

                typing_placeholder.empty()

                first_chunk = False


            # -------------------------------------------------
            # ADD NEW CHUNK
            # -------------------------------------------------

            response_text += chunk


            # -------------------------------------------------
            # SAFE HTML
            # -------------------------------------------------

            safe_stream_text = html.escape(
                response_text
            ).replace(
                "\n",
                "<br>"
            )


            # -------------------------------------------------
            # SHOW STREAMING RESPONSE
            # -------------------------------------------------

            response_placeholder.html(
                f"""
                <div class="chat-row chat-row-assistant">

                    <div class="lumora-avatar">
                        🌿
                    </div>

                    <div class="chat-message-assistant streaming-message">

                        <div class="chat-role-lumora">
                            Lumora
                        </div>

                        <div>
                            {safe_stream_text}
                        </div>

                    </div>

                </div>
                """
            )


    # =====================================================
    # GEMINI ERROR
    # =====================================================

    except Exception as e:

        print(
            f"Lumora streaming API error: {e}"
        )

        typing_placeholder.empty()

        response_placeholder.error(
            "Lumora couldn't generate a reply right now."
        )

        return


    # =====================================================
    # IF NO RESPONSE WAS GENERATED
    # =====================================================

    if not response_text.strip():

        typing_placeholder.empty()

        response_placeholder.error(
            "Lumora couldn't generate a reply right now."
        )

        return


    # =====================================================
    # SAVE FINAL LUMORA RESPONSE
    # =====================================================

    save_message(
        conversation_id,
        "assistant",
        response_text
    )


    # =====================================================
    # BACKGROUND LONG-TERM MEMORY
    # =====================================================

    def save_memory_in_background(
        message
    ):

        try:

            possible_memory = extract_memory(
                message
            )

            if not possible_memory:
                return


            already_exists = (
                long_term_memory_exists(
                    title=possible_memory["title"],
                    content=possible_memory["content"]
                )
            )


            if already_exists:
                return


            save_long_term_memory(
                title=possible_memory["title"],
                content=possible_memory["content"],
                category=possible_memory["category"]
            )


        except Exception as e:

            print(
                f"Lumora background memory error: {e}"
            )


    # =====================================================
    # START MEMORY EXTRACTION AFTER RESPONSE
    # =====================================================

    if safety_result["level"] == "safe":

        import threading

        memory_thread = threading.Thread(
            target=save_memory_in_background,
            args=(user_message,),
            daemon=True
        )

        memory_thread.start()

