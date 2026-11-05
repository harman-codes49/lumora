import streamlit as st

from pathlib import Path
from datetime import date
from html import escape


# =========================================================
# DATABASE
# =========================================================

from app.database.models import (
    save_memory,
    get_memories,
    update_memory,
    delete_memory
)


# =========================================================
# MEMORY STORAGE
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MEMORY_DIR = BASE_DIR / "data" / "memories"

MEMORY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# FULL-SIZE IMAGE DIALOG
# =========================================================

@st.dialog("Your Memory 📸")
def show_full_image(image_path, memory_title):

    st.image(
        str(image_path),
        use_container_width=True
    )

    st.caption(memory_title)

    if st.button(
        "Close",
        use_container_width=True
    ):
        st.rerun()


# =========================================================
# EDIT MEMORY DIALOG
# =========================================================

@st.dialog("Edit Memory ✏️")
def edit_memory_dialog(memory):

    current_title = str(
        memory["title"] or ""
    )

    current_note = str(
        memory["note"] or ""
    )

    current_date = str(
        memory["memory_date"] or ""
    )

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    try:
        selected_date = date.fromisoformat(
            current_date
        )

    except ValueError:
        selected_date = date.today()

    # -----------------------------------------------------
    # EDIT FIELDS
    # -----------------------------------------------------

    new_title = st.text_input(
        "Memory title",
        value=current_title,
        key=f"edit_title_{memory['id']}"
    )

    new_date = st.date_input(
        "When did this happen?",
        value=selected_date,
        key=f"edit_date_{memory['id']}"
    )

    new_note = st.text_area(
        "A little note",
        value=current_note,
        key=f"edit_note_{memory['id']}"
    )

    st.write("")

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # SAVE CHANGES
    # -----------------------------------------------------

    with col1:

        if st.button(
            "💜 Save Changes",
            key=f"save_edit_{memory['id']}",
            use_container_width=True
        ):

            if not new_title.strip():

                st.warning(
                    "Please add a title."
                )

            else:

                update_memory(
                    memory_id=memory["id"],
                    title=new_title.strip(),
                    note=new_note.strip(),
                    memory_date=str(new_date)
                )

                st.success(
                    "Memory updated successfully 💜"
                )

                st.rerun()

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_edit_{memory['id']}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# DELETE MEMORY DIALOG
# =========================================================

@st.dialog("Delete Memory 🗑️")
def delete_memory_dialog(memory):

    memory_title = str(
        memory["title"] or "this memory"
    )

    st.markdown(
        f"""
        Are you sure you want to delete **{escape(memory_title)}**?
        """
    )

    st.caption(
        "This will permanently remove the memory and its "
        "saved photo/video."
    )

    st.write("")

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    with col1:

        if st.button(
            "🗑️ Delete",
            key=f"confirm_delete_{memory['id']}",
            use_container_width=True
        ):

            media_path = memory["media_path"]

            # ---------------------------------------------
            # DELETE MEDIA FILE
            # ---------------------------------------------

            if media_path:

                full_path = BASE_DIR / str(
                    media_path
                ).replace("\\", "/")

                try:

                    if full_path.exists():
                        full_path.unlink()

                except Exception as e:

                    print(
                        f"Lumora media deletion error: {e}"
                    )

            # ---------------------------------------------
            # DELETE DATABASE RECORD
            # ---------------------------------------------

            delete_memory(
                memory["id"]
            )

            st.success(
                "Memory deleted 💜"
            )

            st.rerun()

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_delete_{memory['id']}",
            use_container_width=True
        ):

            st.rerun()


# =========================================================
# MEMORIES PAGE
# =========================================================

def render_memories():

    # =====================================================
    # PAGE STYLING
    # =====================================================

    st.html("""
    <style>

    .memory-page {
        padding: 20px 0 10px 0;
    }

    .memory-heading {
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        color: #403858;
        margin-bottom: 5px;
    }

    .memory-subheading {
        color: #81788e;
        font-size: 13px;
        margin-bottom: 25px;
    }

    .memory-card {
        background: #ffffff;
        border: 1px solid #eee7f3;
        border-radius: 22px;
        padding: 20px;
        margin: 25px 0 8px 0;
        box-shadow: 0 4px 18px rgba(80, 65, 100, 0.05);
    }

    .memory-title {
        font-family: 'Playfair Display', serif;
        font-size: 20px;
        color: #403858;
        margin-bottom: 5px;
    }

    .memory-date {
        color: #9a90a5;
        font-size: 11px;
        margin-bottom: 10px;
    }

    .memory-note {
        color: #665d70;
        font-size: 13px;
        line-height: 1.6;
    }

    .memory-count {
        display: inline-block;
        background: #f1eafa;
        color: #66558a;
        border-radius: 20px;
        padding: 6px 12px;
        font-size: 11px;
        margin-bottom: 18px;
    }

    .memory-thumbnail {
        width: 260px;
        height: 180px;
        object-fit: cover;
        border-radius: 16px;
        display: block;
        margin-top: 14px;
        box-shadow: 0 3px 12px rgba(80, 65, 100, 0.08);
    }

    .memory-hint {
        color: #9a90a5;
        font-size: 10px;
        margin-top: 6px;
        margin-bottom: 8px;
    }

    .memory-menu {
        text-align: right;
    }

    .empty-memory {
        text-align: center;
        padding: 65px 20px;
        background: #f8f4fb;
        border-radius: 25px;
        margin-top: 20px;
    }

    .empty-icon {
        font-size: 42px;
        margin-bottom: 12px;
    }

    .empty-title {
        font-family: 'Playfair Display', serif;
        font-size: 23px;
        color: #403858;
    }

    .empty-text {
        color: #81788e;
        font-size: 13px;
        margin-top: 8px;
    }

    </style>
    """)


    # =====================================================
    # PAGE HEADER
    # =====================================================

    st.html("""
    <div class="memory-page">

        <div class="memory-heading">
            Your Memories 📸
        </div>

        <div class="memory-subheading">
            Keep the little moments that matter close. 💜
        </div>

    </div>
    """)


    # =====================================================
    # ADD MEMORY
    # =====================================================

    with st.expander(
        "＋ Add a New Memory",
        expanded=True
    ):

        title = st.text_input(
            "Memory title",
            placeholder="e.g. College farewell 💜"
        )

        memory_date = st.date_input(
            "When did this happen?",
            value=date.today()
        )

        note = st.text_area(
            "A little note",
            placeholder="Write something you'd like to remember..."
        )

        uploaded_file = st.file_uploader(
            "Add a photo or video",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
                "mp4",
                "mov",
                "avi"
            ]
        )

        save_button = st.button(
            "Save Memory 💜",
            use_container_width=True
        )


        # =================================================
        # SAVE MEMORY
        # =================================================

        if save_button:

            if not title.strip():

                st.warning(
                    "Please add a title for your memory."
                )

            else:

                media_path = ""


                # =========================================
                # SAVE MEDIA
                # =========================================

                if uploaded_file is not None:

                    original_name = Path(
                        uploaded_file.name
                    ).name

                    safe_filename = (
                        original_name
                        .replace(" ", "_")
                    )

                    file_path = (
                        MEMORY_DIR / safe_filename
                    )


                    with open(
                        file_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )


                    media_path = str(
                        file_path.relative_to(
                            BASE_DIR
                        ).as_posix()
                    )


                # =========================================
                # SAVE TO DATABASE
                # =========================================

                save_memory(
                    title=title.strip(),
                    note=note.strip(),
                    media_path=media_path,
                    memory_date=str(memory_date)
                )


                st.success(
                    "Memory saved successfully 💜"
                )

                st.rerun()


    # =====================================================
    # LOAD MEMORIES
    # =====================================================

    memories = get_memories()


    # =====================================================
    # MEMORY COUNT
    # =====================================================

    if memories:

        count_text = (
            "moment"
            if len(memories) == 1
            else "moments"
        )

        st.html(
            f"""
            <div class="memory-count">
                💜 {len(memories)} saved {count_text}
            </div>
            """
        )


    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not memories:

        st.html("""
        <div class="empty-memory">

            <div class="empty-icon">
                📸
            </div>

            <div class="empty-title">
                No memories yet
            </div>

            <div class="empty-text">
                Save a little moment that you would
                like Lumora to keep close.
            </div>

        </div>
        """)

        return


    # =====================================================
    # DISPLAY MEMORIES
    # =====================================================

    for memory in memories:

        # -------------------------------------------------
        # RAW VALUES
        # -------------------------------------------------

        raw_title = str(
            memory["title"] or ""
        )

        raw_note = str(
            memory["note"] or ""
        )

        raw_date = str(
            memory["memory_date"] or ""
        )


        # -------------------------------------------------
        # SAFE HTML VALUES
        # -------------------------------------------------

        memory_title = escape(
            raw_title
        )

        memory_note = escape(
            raw_note
        ).replace(
            "\n",
            "<br>"
        )

        memory_date = escape(
            raw_date
        )


        # =================================================
        # MEMORY HEADER + THREE DOT MENU
        # =================================================

        col1, col2 = st.columns(
            [0.92, 0.08],
            vertical_alignment="top"
        )


        # -------------------------------------------------
        # LEFT SIDE
        # -------------------------------------------------

        with col1:

            st.html(
                f"""
                <div class="memory-card">

                    <div class="memory-title">
                        {memory_title}
                    </div>

                    <div class="memory-date">
                        📅 {memory_date}
                    </div>

                    <div class="memory-note">
                        {memory_note}
                    </div>

                </div>
                """
            )


        # -------------------------------------------------
        # THREE DOT MENU
        # -------------------------------------------------

        with col2:

            with st.popover(
                "⋯",
                use_container_width=True
            ):

                st.markdown(
                    "**Memory options**"
                )

                if st.button(
                    "✏️ Edit",
                    key=f"edit_memory_{memory['id']}",
                    use_container_width=True
                ):

                    edit_memory_dialog(
                        memory
                    )

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_memory_{memory['id']}",
                    use_container_width=True
                ):

                    delete_memory_dialog(
                        memory
                    )


        # =================================================
        # MEDIA
        # =================================================

        media_path = memory["media_path"]


        if media_path:

            full_path = BASE_DIR / str(
                media_path
            ).replace("\\", "/")


            if full_path.exists():

                suffix = full_path.suffix.lower()


                # =========================================
                # IMAGE
                # =========================================

                if suffix in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                ]:

                    # -------------------------------------
                    # SMALL THUMBNAIL
                    # -------------------------------------

                    st.image(
                        str(full_path),
                        width=260
                    )


                    st.html("""
                    <div class="memory-hint">
                        Tap below to view the full-size memory 💜
                    </div>
                    """)


                    # -------------------------------------
                    # FULL SIZE BUTTON
                    # -------------------------------------

                    if st.button(
                        "🔍 View Full Size",
                        key=f"view_memory_{memory['id']}"
                    ):

                        show_full_image(
                            full_path,
                            raw_title
                        )


                # =========================================
                # VIDEO
                # =========================================

                elif suffix in [
                    ".mp4",
                    ".mov",
                    ".avi"
                ]:

                    st.video(
                        str(full_path)
                    )

        # Small spacing between memories
        st.write("")