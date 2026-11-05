import html
import streamlit as st

from app.database.models import (
    get_long_term_memories,
    update_long_term_memory,
    delete_long_term_memory,
    delete_all_long_term_memories,
    get_important_dates,
    update_important_date,
    delete_important_date,
)


# =========================================================
# CSS
# =========================================================

_SPACE_CSS = ("""
<style>

.space-header {
    padding: 10px 0 24px 0;
}

.space-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    color: #403858;
}

.space-subtitle {
    color: #8b8192;
    font-size: 13px;
    margin-top: 5px;
}

.space-card {
    background: #ffffff;
    border: 1px solid #eee5f2;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 3px 15px rgba(80, 65, 100, 0.03);
}

.memory-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    color: #403858;
}

.memory-content {
    color: #6f6679;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 7px;
}

.memory-category {
    color: #9a8ea4;
    font-size: 11px;
    margin-top: 8px;
}

.section-heading {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: #403858;
    margin-top: 20px;
    margin-bottom: 12px;
}

.empty-space {
    background: #f7f0fa;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    color: #81788e;
}

</style>
""")


# =========================================================
# EDIT MEMORY
# =========================================================

@st.dialog("Edit Memory 🧠")
def edit_memory_dialog(memory_id, title, content):

    st.write("Update what Lumora remembers.")

    new_title = st.text_input(
        "Memory title",
        value=title,
        key=f"edit_title_{memory_id}"
    )

    new_content = st.text_area(
        "Memory",
        value=content,
        key=f"edit_content_{memory_id}",
        height=120
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💜 Save Changes",
            key=f"save_edit_{memory_id}",
            use_container_width=True
        ):

            if new_title.strip() and new_content.strip():

                update_long_term_memory(
                    memory_id,
                    new_title.strip(),
                    new_content.strip()
                )

                st.success("Memory updated. 💜")

                st.rerun()

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_edit_{memory_id}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# DELETE MEMORY
# =========================================================

@st.dialog("Delete Memory")
def delete_memory_dialog(memory_id, title):

    st.write(
        f'Are you sure you want to delete "{title}"?'
    )

    st.caption(
        "Lumora will no longer use this memory in future conversations."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ Delete",
            key=f"confirm_delete_{memory_id}",
            use_container_width=True
        ):

            delete_long_term_memory(
                memory_id
            )

            st.success("Memory deleted.")

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_delete_{memory_id}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# DELETE ALL
# =========================================================

@st.dialog("Delete All Memories")
def delete_all_memories_dialog():

    st.write(
        "Are you sure you want to delete all of your saved memories?"
    )

    st.caption(
        "This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ Delete Everything",
            key="confirm_delete_all",
            use_container_width=True
        ):

            delete_all_long_term_memories()

            st.success(
                "All long-term memories have been deleted."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            key="cancel_delete_all",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# EDIT DATE
# =========================================================

@st.dialog("Edit Important Date 📅")
def edit_date_dialog(
    date_id,
    title,
    date_value,
    note,
    reminder_enabled
):

    st.write("Update this important date.")

    new_title = st.text_input(
        "Title",
        value=title,
        key=f"date_title_{date_id}"
    )

    new_date = st.date_input(
        "Date",
        value=__import__("datetime").date.fromisoformat(
            str(date_value)
        ),
        key=f"date_value_{date_id}"
    )

    new_note = st.text_area(
        "Note",
        value=note or "",
        key=f"date_note_{date_id}"
    )

    new_reminder = st.checkbox(
        "🔔 Remind me",
        value=bool(reminder_enabled),
        key=f"date_reminder_{date_id}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💜 Save Changes",
            key=f"save_date_edit_{date_id}",
            use_container_width=True
        ):

            update_important_date(
                date_id=date_id,
                title=new_title.strip(),
                date=str(new_date),
                note=new_note.strip(),
                reminder_enabled=new_reminder
            )

            st.success("Important date updated.")

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_date_edit_{date_id}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# DELETE DATE
# =========================================================

@st.dialog("Delete Important Date")
def delete_date_dialog(date_id, title):

    st.write(
        f'Delete "{title}" from your important dates?'
    )

    st.caption(
        "Its reminder will also stop."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ Delete",
            key=f"delete_date_{date_id}",
            use_container_width=True
        ):

            delete_important_date(
                date_id
            )

            st.success(
                "Important date deleted."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_date_{date_id}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# YOUR SPACE
# =========================================================

def render_space():
    st.html(_SPACE_CSS)


    st.html("""
    <div class="space-header">

        <div class="space-title">
            Your Space 👤
        </div>

        <div class="space-subtitle">
            A place for the things Lumora remembers about you.
        </div>

    </div>
    """)

    # =====================================================
    # LONG-TERM MEMORIES
    # =====================================================

    st.html("""
    <div class="section-heading">
        🧠 What Lumora Remembers
    </div>
    """)

    memories = get_long_term_memories()

    if memories:

        col1, col2 = st.columns([4, 1])

        with col2:

            if st.button(
                "🗑️ Delete All",
                key="delete_all_memories",
                use_container_width=True
            ):

                delete_all_memories_dialog()

        for memory in memories:

            memory_id = memory["id"]
            title = str(memory["title"])
            content = str(memory["note"])

            category = str(memory["category"] or "general")

            st.html(f"""
            <div class="space-card">

                <div class="memory-title">
                    🧠 {html.escape(title)}
                </div>

                <div class="memory-content">
                    {html.escape(content)}
                </div>

                <div class="memory-category">
                    Saved as a {html.escape(category)} memory
                </div>

            </div>
            """)

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✏️ Edit",
                    key=f"edit_memory_{memory_id}",
                    use_container_width=True
                ):

                    edit_memory_dialog(
                        memory_id,
                        title,
                        content
                    )

            with col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_memory_button_{memory_id}",
                    use_container_width=True
                ):

                    delete_memory_dialog(
                        memory_id,
                        title
                    )

    else:

        st.html("""
        <div class="empty-space">

            🧠 Lumora hasn't saved any long-term memories yet.

            <br><br>

            As you talk naturally, Lumora may remember
            useful preferences, goals and habits.

        </div>
        """)

    # =====================================================
    # IMPORTANT DATES
    # =====================================================

    st.html("""
    <div class="section-heading">
        📅 Important Dates
    </div>
    """)

    dates = get_important_dates()

    if dates:

        for item in dates:

            date_id = item["id"]
            title = str(item["title"])
            date_value = str(item["date"])
            note = str(item["note"] or "")
            reminder_enabled = item["reminder_enabled"]

            st.html(f"""
            <div class="space-card">

                <div class="memory-title">
                    📅 {html.escape(title)}
                </div>

                <div class="memory-content">
                    {html.escape(date_value)}
                </div>

                <div class="memory-content">
                    {html.escape(note)}
                </div>

            </div>
            """)

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✏️ Edit Date",
                    key=f"edit_date_button_{date_id}",
                    use_container_width=True
                ):

                    edit_date_dialog(
                        date_id,
                        title,
                        date_value,
                        note,
                        reminder_enabled
                    )

            with col2:

                if st.button(
                    "🗑️ Delete Date",
                    key=f"delete_date_button_{date_id}",
                    use_container_width=True
                ):

                    delete_date_dialog(
                        date_id,
                        title
                    )

    else:

        st.html("""
        <div class="empty-space">

            📅 No important dates saved yet.

            <br><br>

            Dates detected in conversations are only saved
            after you confirm them.

        </div>
        """)