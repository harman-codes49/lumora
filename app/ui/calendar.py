import streamlit as st
from datetime import date
from html import escape

from app.database.models import (
    save_important_date,
    get_important_dates
)


# =========================================================
# CALENDAR PAGE
# =========================================================

def render_calendar():

    # =====================================================
    # STYLING
    # =====================================================

    st.html("""
    <style>

    .calendar-page {
        padding: 20px 0 10px 0;
    }

    .calendar-heading {
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        color: #403858;
        margin-bottom: 5px;
    }

    .calendar-subheading {
        color: #81788e;
        font-size: 13px;
        margin-bottom: 25px;
    }

    .date-card {
        background: #ffffff;
        border: 1px solid #eee7f3;
        border-radius: 20px;
        padding: 18px 20px;
        margin: 15px 0;
        box-shadow: 0 4px 18px rgba(80, 65, 100, 0.05);
    }

    .date-title {
        font-family: 'Playfair Display', serif;
        font-size: 19px;
        color: #403858;
    }

    .date-value {
        color: #7b6c91;
        font-size: 12px;
        margin-top: 5px;
    }

    .date-note {
        color: #665d70;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 8px;
    }

    .reminder-on {
        display: inline-block;
        margin-top: 10px;
        padding: 5px 10px;
        border-radius: 15px;
        background: #f1eafa;
        color: #66558a;
        font-size: 10px;
    }

    .empty-calendar {
        text-align: center;
        padding: 60px 20px;
        background: #f8f4fb;
        border-radius: 25px;
        margin-top: 20px;
    }

    .empty-calendar-icon {
        font-size: 42px;
    }

    .empty-calendar-title {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        color: #403858;
        margin-top: 10px;
    }

    .empty-calendar-text {
        color: #81788e;
        font-size: 13px;
        margin-top: 7px;
    }

    </style>
    """)


    # =====================================================
    # HEADER
    # =====================================================

    st.html("""
    <div class="calendar-page">

        <div class="calendar-heading">
            Important Dates 📅
        </div>

        <div class="calendar-subheading">
            Keep the dates that matter close. Lumora will help
            you remember them. 💜
        </div>

    </div>
    """)


    # =====================================================
    # ADD DATE
    # =====================================================

    with st.expander(
        "＋ Add an Important Date",
        expanded=True
    ):

        title = st.text_input(
            "What is the occasion?",
            placeholder="e.g. Mom's Birthday 🎂"
        )

        important_date = st.date_input(
            "Date",
            value=date.today()
        )

        note = st.text_area(
            "A little note",
            placeholder="Why is this date important?"
        )

        reminder_enabled = st.checkbox(
            "🔔 Remind me about this date",
            value=True
        )

        save_button = st.button(
            "Save Important Date 💜",
            use_container_width=True
        )


        # =================================================
        # SAVE
        # =================================================

        if save_button:

            if not title.strip():

                st.warning(
                    "Please add a title for this date."
                )

            else:

                save_important_date(
                    title=title.strip(),
                    date=str(important_date),
                    note=note.strip(),
                    reminder_enabled=reminder_enabled
                )

                st.success(
                    "Important date saved 💜"
                )

                st.rerun()


    # =====================================================
    # LOAD DATES
    # =====================================================

    important_dates = get_important_dates()


    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not important_dates:

        st.html("""
        <div class="empty-calendar">

            <div class="empty-calendar-icon">
                📅
            </div>

            <div class="empty-calendar-title">
                No important dates yet
            </div>

            <div class="empty-calendar-text">
                Add birthdays, anniversaries, milestones,
                or any date you never want to forget.
            </div>

        </div>
        """)

        return


    # =====================================================
    # DISPLAY DATES
    # =====================================================

    for item in important_dates:

        title = escape(
            str(item["title"] or "")
        )

        item_date = escape(
            str(item["date"] or "")
        )

        note = escape(
            str(item["note"] or "")
        ).replace(
            "\n",
            "<br>"
        )

        reminder_enabled = item["reminder_enabled"]


        st.html(
            f"""
            <div class="date-card">

                <div class="date-title">
                    {title}
                </div>

                <div class="date-value">
                    📅 {item_date}
                </div>

                <div class="date-note">
                    {note}
                </div>

                {
                    '<div class="reminder-on">🔔 Reminder enabled</div>'
                    if reminder_enabled
                    else ''
                }

            </div>
            """
        )