import streamlit as st
from datetime import date
from html import escape

from app.database.db import get_connection


# =========================================================
# DATABASE
# =========================================================

def initialize_reflection_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reflection_date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_reflection(
    reflection_date,
    prompt,
    response
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reflections
        (
            reflection_date,
            prompt,
            response
        )
        VALUES (?, ?, ?)
        """,
        (
            reflection_date,
            prompt,
            response
        )
    )

    connection.commit()
    connection.close()


def get_reflections():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM reflections
        ORDER BY reflection_date DESC, created_at DESC
        """
    )

    reflections = cursor.fetchall()

    connection.close()

    return reflections


def delete_reflection(reflection_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM reflections
        WHERE id = ?
        """,
        (reflection_id,)
    )

    connection.commit()
    connection.close()


# =========================================================
# REFLECTION PAGE
# =========================================================

def render_reflection():

    initialize_reflection_table()

    # =====================================================
    # PAGE CSS
    # =====================================================

    st.html(
        """
        <style>

        .reflection-page {
            padding: 20px 0 10px 0;
        }

        .reflection-heading {
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            color: #403858;
            margin-bottom: 5px;
        }

        .reflection-subheading {
            color: #81788e;
            font-size: 13px;
            margin-bottom: 25px;
        }

        .reflection-intro {
            background: linear-gradient(
                135deg,
                #f0e8f6,
                #faf5f8
            );
            border-radius: 24px;
            padding: 24px 26px;
            margin-bottom: 25px;
        }

        .reflection-intro-title {
            font-family: 'Playfair Display', serif;
            font-size: 21px;
            color: #403858;
        }

        .reflection-intro-text {
            color: #70667a;
            font-size: 13px;
            line-height: 1.6;
            margin-top: 8px;
        }

        .reflection-card {
            background: #ffffff;
            border: 1px solid #eee7f3;
            border-radius: 22px;
            padding: 22px;
            margin-top: 18px;
            box-shadow: 0 4px 18px rgba(
                80,
                65,
                100,
                0.05
            );
        }

        .reflection-card-date {
            color: #9a90a5;
            font-size: 11px;
            margin-bottom: 10px;
        }

        .reflection-card-prompt {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            color: #403858;
            margin-bottom: 9px;
        }

        .reflection-card-response {
            color: #665d70;
            font-size: 13px;
            line-height: 1.7;
        }

        .reflection-empty {
            text-align: center;
            padding: 55px 20px;
            background: #f8f4fb;
            border-radius: 24px;
            margin-top: 22px;
        }

        .reflection-empty-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }

        .reflection-empty-title {
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            color: #403858;
        }

        .reflection-empty-text {
            color: #81788e;
            font-size: 13px;
            margin-top: 7px;
        }

        </style>
        """
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.html(
        """
        <div class="reflection-page">

            <div class="reflection-heading">
                Daily Reflection 🌱
            </div>

            <div class="reflection-subheading">
                A quiet space to pause, notice and understand yourself.
            </div>

        </div>
        """
    )

    # =====================================================
    # INTRO
    # =====================================================

    st.html(
        """
        <div class="reflection-intro">

            <div class="reflection-intro-title">
                Take a little moment for yourself 💜
            </div>

            <div class="reflection-intro-text">
                There is no right or wrong answer here.
                Write whatever feels useful today — even
                if it is only a few words.
            </div>

        </div>
        """
    )

    # =====================================================
    # REFLECTION PROMPTS
    # =====================================================

    prompts = [
        "How was your day today?",
        "What is on your mind right now?",
        "What went well today?",
        "What felt difficult today?",
        "What do you want to carry into tomorrow?"
    ]

    # =====================================================
    # NEW REFLECTION
    # =====================================================

    with st.form("reflection_form"):

        reflection_date = st.date_input(
            "Reflection date",
            value=date.today()
        )

        selected_prompt = st.selectbox(
            "Choose a reflection prompt",
            prompts
        )

        response = st.text_area(
            "Your reflection",
            placeholder=(
                "Write whatever comes to mind..."
            ),
            height=180
        )

        save_button = st.form_submit_button(
            "Save Reflection 💜",
            use_container_width=True
        )

    # =====================================================
    # SAVE
    # =====================================================

    if save_button:

        if not response.strip():

            st.warning(
                "Write something before saving your reflection."
            )

        else:

            save_reflection(
                reflection_date=str(
                    reflection_date
                ),
                prompt=selected_prompt,
                response=response.strip()
            )

            st.success(
                "Your reflection has been saved. 💜"
            )

            st.rerun()

    # =====================================================
    # PREVIOUS REFLECTIONS
    # =====================================================

    st.html(
        """
        <div style="
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            color: #403858;
            margin-top: 35px;
            margin-bottom: 8px;
        ">
            Your Reflections
        </div>
        """
    )

    reflections = get_reflections()

    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not reflections:

        st.html(
            """
            <div class="reflection-empty">

                <div class="reflection-empty-icon">
                    🌱
                </div>

                <div class="reflection-empty-title">
                    Your reflection space is empty
                </div>

                <div class="reflection-empty-text">
                    Your first reflection can start with
                    just a few honest words.
                </div>

            </div>
            """
        )

        return

    # =====================================================
    # DISPLAY REFLECTIONS
    # =====================================================

    for reflection in reflections:

        reflection_id = reflection["id"]

        reflection_date = escape(
            str(
                reflection["reflection_date"]
                or ""
            )
        )

        prompt = escape(
            str(
                reflection["prompt"]
                or ""
            )
        )

        reflection_response = escape(
            str(
                reflection["response"]
                or ""
            )
        ).replace(
            "\n",
            "<br>"
        )

        st.html(
            f"""
            <div class="reflection-card">

                <div class="reflection-card-date">
                    📅 {reflection_date}
                </div>

                <div class="reflection-card-prompt">
                    {prompt}
                </div>

                <div class="reflection-card-response">
                    {reflection_response}
                </div>

            </div>
            """
        )

        if st.button(
            "Delete",
            key=f"delete_reflection_{reflection_id}"
        ):

            delete_reflection(
                reflection_id
            )

            st.success(
                "Reflection deleted."
            )

            st.rerun()