import html
import streamlit as st

from app.database.models import (
    get_conversations,
    get_messages,
    get_memories,
    get_long_term_memories,
)


def _safe(value):
    return html.escape(str(value or ""))


def _contains(query, *values):
    query = query.lower().strip()
    if not query:
        return True
    return any(query in str(value or "").lower() for value in values)


def _open_conversation(conversation_id):
    st.session_state.current_conversation_id = conversation_id
    st.session_state.pending_date_suggestions = []
    st.session_state.page = "chat"
    st.rerun()


def _open_memories():
    st.session_state.page = "memories"
    st.rerun()


def _render_result_card(icon, title, text, meta, button_label, button_key, callback):
    st.html(f"""
    <div class="search-result-card">
        <div class="search-result-icon">{icon}</div>
        <div class="search-result-body">
            <div class="search-result-title">{_safe(title)}</div>
            <div class="search-result-text">{_safe(text)}</div>
            <div class="search-result-meta">{_safe(meta)}</div>
        </div>
    </div>
    """)

    if st.button(
        button_label,
        key=button_key,
        use_container_width=True,
    ):
        callback()


def render_search():
    st.html("""
    <style>
    .search-header {
        padding: 8px 0 20px 0;
    }

    .search-title {
        font-family: 'Playfair Display', serif;
        font-size: 30px;
        color: #403858;
    }

    .search-subtitle {
        color: #8b8192;
        font-size: 13px;
        margin-top: 4px;
    }

    .search-tip {
        background: #f7f0fa;
        border: 1px solid #e8dced;
        border-radius: 18px;
        padding: 14px 17px;
        color: #71677c;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .search-result-card {
        display: flex;
        gap: 14px;
        align-items: flex-start;
        background: #ffffff;
        border: 1px solid #eee7f3;
        border-radius: 18px;
        padding: 16px;
        margin: 8px 0 6px 0;
        box-shadow: 0 3px 12px rgba(80, 65, 100, 0.03);
    }

    .search-result-icon {
        font-size: 22px;
        width: 38px;
        height: 38px;
        border-radius: 13px;
        background: #eee7f5;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .search-result-title {
        color: #403858;
        font-weight: 600;
        font-size: 15px;
    }

    .search-result-text {
        color: #71677c;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 4px;
    }

    .search-result-meta {
        color: #9a8ea4;
        font-size: 11px;
        margin-top: 7px;
    }

    .search-empty {
        text-align: center;
        padding: 55px 20px;
        color: #8b8192;
    }

    .search-empty-icon {
        font-size: 34px;
        margin-bottom: 10px;
    }

    .search-empty-title {
        font-family: 'Playfair Display', serif;
        color: #403858;
        font-size: 22px;
    }
    </style>
    """)

    st.html("""
    <div class="search-header">
        <div class="search-title">Search your Lumora space 🔍</div>
        <div class="search-subtitle">
            Find conversations, saved memories and things Lumora remembers about you.
        </div>
    </div>
    """)

    st.html("""
    <div class="search-tip">
        💜 Try words like <b>Java</b>, <b>college</b>, <b>birthday</b>,
        <b>placement</b>, or a conversation topic.
    </div>
    """)

    query = st.text_input(
        "",
        placeholder="Search conversations, memories, topics...",
        label_visibility="collapsed",
        key="lumora_search_query",
    )

    query = query.strip()

    if not query:
        st.html("""
        <div class="search-empty">
            <div class="search-empty-icon">🔎</div>
            <div class="search-empty-title">What are you looking for?</div>
            <div>Search across your Lumora space using a word or phrase.</div>
        </div>
        """)
        return

    conversations = get_conversations()
    media_memories = get_memories()
    long_term_memories = get_long_term_memories()

    conversation_results = []
    memory_results = []
    long_term_results = []

    for conversation in conversations:
        conversation_id = conversation["id"]
        title = conversation["title"] or "New Conversation"

        if _contains(query, title):
            conversation_results.append({
                "id": conversation_id,
                "title": title,
                "text": "Conversation title matches your search.",
                "meta": "Conversation",
            })
            continue

        try:
            messages = get_messages(conversation_id)
        except Exception:
            messages = []

        for message in messages:
            content = str(message["content"] or "")

            if query.lower() in content.lower():
                snippet = content.replace("\n", " ").strip()
                if len(snippet) > 180:
                    snippet = snippet[:180] + "..."

                conversation_results.append({
                    "id": conversation_id,
                    "title": title,
                    "text": snippet,
                    "meta": "Message match",
                })
                break

    for memory in media_memories:
        title = memory["title"] or "Saved Memory"
        note = memory["note"] or ""
        date = memory["memory_date"] or ""

        if _contains(query, title, note, date):
            text = note if note else "A saved photo or video memory."
            memory_results.append({
                "id": memory["id"],
                "title": title,
                "text": text,
                "meta": f"Saved memory{(' • ' + str(date)) if date else ''}",
            })

    for memory in long_term_memories:
        title = memory["title"] or "Lumora memory"
        content = memory["note"] or ""
        category = memory["category"] or "general"

        if _contains(query, title, content, category):
            long_term_results.append({
                "id": memory["id"],
                "title": title,
                "text": content,
                "meta": f"{category.title()} memory",
            })

    total = len(conversation_results) + len(memory_results) + len(long_term_results)

    st.caption(f"{total} result{'s' if total != 1 else ''} found")

    if conversation_results:
        st.html("<div class='section-title'>💬 Conversations</div>")

        for index, result in enumerate(conversation_results):
            _render_result_card(
                "💬",
                result["title"],
                result["text"],
                result["meta"],
                "Open conversation →",
                f"search_open_conversation_{result['id']}_{index}",
                lambda conversation_id=result["id"]: _open_conversation(conversation_id),
            )

    if memory_results:
        st.html("<div class='section-title'>📸 Saved Memories</div>")

        for index, result in enumerate(memory_results):
            _render_result_card(
                "📸",
                result["title"],
                result["text"],
                result["meta"],
                "Open Memories →",
                f"search_open_media_{result['id']}_{index}",
                _open_memories,
            )

    if long_term_results:
        st.html("<div class='section-title'>🧠 What Lumora Remembers</div>")

        for result in long_term_results:
            st.html(f"""
            <div class="search-result-card">
                <div class="search-result-icon">🧠</div>
                <div class="search-result-body">
                    <div class="search-result-title">{_safe(result['title'])}</div>
                    <div class="search-result-text">{_safe(result['text'])}</div>
                    <div class="search-result-meta">{_safe(result['meta'])}</div>
                </div>
            </div>
            """)

    if total == 0:
        st.html(f"""
        <div class="search-empty">
            <div class="search-empty-icon">🌿</div>
            <div class="search-empty-title">No matches found</div>
            <div>Try a different word or a shorter phrase.</div>
        </div>
        """)
