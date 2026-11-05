import streamlit as st
from collections import Counter
from datetime import datetime
from html import escape

from app.database.db import get_connection


# =========================================================
# REFLECTION DATA
# =========================================================

def get_reflection_insights_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            reflection_date,
            prompt,
            response,
            created_at
        FROM reflections
        ORDER BY reflection_date ASC, created_at ASC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# =========================================================
# HELPERS
# =========================================================

def format_date(value):

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).strftime("%d %b %Y")
    except Exception:
        return str(value)


def build_activity_data(reflections):

    activity = Counter()

    for reflection in reflections:

        reflection_date = str(
            reflection["reflection_date"] or ""
        )

        if reflection_date:
            activity[reflection_date] += 1

    return activity


# =========================================================
# PAGE
# =========================================================

def render_mood_insights():

    st.html(
        """
        <style>

        .insights-header {
            padding: 20px 0 8px 0;
        }

        .insights-title {
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            color: #403858;
        }

        .insights-subtitle {
            color: #81788e;
            font-size: 13px;
            margin-top: 5px;
        }

        .insights-intro {
            background: linear-gradient(
                135deg,
                #f0e8f6,
                #faf5f8
            );
            border-radius: 24px;
            padding: 24px 26px;
            margin: 20px 0 25px 0;
        }

        .insights-intro-title {
            font-family: 'Playfair Display', serif;
            font-size: 21px;
            color: #403858;
        }

        .insights-intro-text {
            color: #70667a;
            font-size: 13px;
            line-height: 1.7;
            margin-top: 8px;
        }

        .insight-card {
            background: #ffffff;
            border: 1px solid #eee7f3;
            border-radius: 22px;
            padding: 22px;
            min-height: 135px;
            box-shadow: 0 4px 18px rgba(80,65,100,0.05);
        }

        .insight-icon {
            font-size: 23px;
        }

        .insight-number {
            font-family: 'Playfair Display', serif;
            font-size: 27px;
            color: #403858;
            margin-top: 8px;
        }

        .insight-label {
            color: #81788e;
            font-size: 12px;
            margin-top: 3px;
        }

        .section-heading {
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            color: #403858;
            margin-top: 32px;
            margin-bottom: 12px;
        }

        .gentle-card {
            background: #f5eef9;
            border-radius: 22px;
            padding: 22px 24px;
            margin-top: 20px;
        }

        .gentle-title {
            font-family: 'Playfair Display', serif;
            color: #403858;
            font-size: 19px;
        }

        .gentle-text {
            color: #70667a;
            font-size: 13px;
            line-height: 1.7;
            margin-top: 8px;
        }

        .recent-card {
            background: #ffffff;
            border: 1px solid #eee7f3;
            border-radius: 18px;
            padding: 17px 20px;
            margin-top: 12px;
        }

        .recent-date {
            color: #9a90a5;
            font-size: 11px;
        }

        .recent-prompt {
            font-family: 'Playfair Display', serif;
            color: #403858;
            font-size: 17px;
            margin-top: 5px;
        }

        .recent-preview {
            color: #70667a;
            font-size: 12px;
            line-height: 1.6;
            margin-top: 7px;
        }

        .empty-insights {
            text-align: center;
            padding: 65px 20px;
            background: #f8f4fb;
            border-radius: 24px;
            margin-top: 25px;
        }

        .empty-icon {
            font-size: 42px;
        }

        .empty-title {
            font-family: 'Playfair Display', serif;
            font-size: 23px;
            color: #403858;
            margin-top: 10px;
        }

        .empty-text {
            color: #81788e;
            font-size: 13px;
            margin-top: 7px;
        }

        </style>
        """
    )

    st.html(
        """
        <div class="insights-header">

            <div class="insights-title">
                Mood Insights 🌱
            </div>

            <div class="insights-subtitle">
                Notice your reflection patterns over time,
                without turning them into a diagnosis.
            </div>

        </div>

        <div class="insights-intro">

            <div class="insights-intro-title">
                A little more awareness, not a label 💜
            </div>

            <div class="insights-intro-text">
                Lumora currently uses your saved reflections to
                show simple patterns such as reflection frequency
                and the topics you choose to write about. It does
                not diagnose emotions or mental-health conditions.
            </div>

        </div>
        """
    )

    reflections = get_reflection_insights_data()

    if not reflections:

        st.html(
            """
            <div class="empty-insights">

                <div class="empty-icon">
                    🌱
                </div>

                <div class="empty-title">
                    Your insights will grow with you
                </div>

                <div class="empty-text">
                    Save a few daily reflections first.
                    Lumora will then show your reflection
                    patterns here.
                </div>

            </div>
            """
        )

        return

    total_reflections = len(reflections)

    unique_days = len(
        {
            str(row["reflection_date"])
            for row in reflections
            if row["reflection_date"]
        }
    )

    prompt_counts = Counter(
        str(row["prompt"])
        for row in reflections
        if row["prompt"]
    )

    most_used_prompt = (
        prompt_counts.most_common(1)[0][0]
        if prompt_counts
        else "—"
    )

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.html(
            f"""
            <div class="insight-card">

                <div class="insight-icon">📝</div>

                <div class="insight-number">
                    {total_reflections}
                </div>

                <div class="insight-label">
                    Total reflections
                </div>

            </div>
            """
        )

    with col2:
        st.html(
            f"""
            <div class="insight-card">

                <div class="insight-icon">📅</div>

                <div class="insight-number">
                    {unique_days}
                </div>

                <div class="insight-label">
                    Days you reflected
                </div>

            </div>
            """
        )

    with col3:
        st.html(
            f"""
            <div class="insight-card">

                <div class="insight-icon">🌱</div>

                <div class="insight-number">
                    {len(prompt_counts)}
                </div>

                <div class="insight-label">
                    Reflection prompts explored
                </div>

            </div>
            """
        )

    # =====================================================
    # REFLECTION ACTIVITY
    # =====================================================

    st.html(
        """
        <div class="section-heading">
            Reflection Activity 📈
        </div>
        """
    )

    activity = build_activity_data(reflections)

    if activity:

        activity_data = {
            "Date": list(activity.keys()),
            "Reflections": list(activity.values())
        }

        st.bar_chart(
            activity_data,
            x="Date",
            y="Reflections",
            use_container_width=True
        )

    # =====================================================
    # MOST USED PROMPT
    # =====================================================

    st.html(
        f"""
        <div class="gentle-card">

            <div class="gentle-title">
                Something to notice 💭
            </div>

            <div class="gentle-text">
                You have used
                <b>{escape(most_used_prompt)}</b>
                most often among your saved reflection prompts.
                That may simply mean this question feels useful
                for you to think about.
            </div>

        </div>
        """
    )

    # =====================================================
    # RECENT REFLECTIONS
    # =====================================================

    st.html(
        """
        <div class="section-heading">
            Recent Reflections 🌿
        </div>
        """
    )

    recent_reflections = list(reversed(reflections[-5:]))

    for reflection in recent_reflections:

        reflection_date = escape(
            format_date(
                reflection["reflection_date"]
            )
        )

        prompt = escape(
            str(reflection["prompt"] or "")
        )

        response = str(
            reflection["response"] or ""
        ).strip()

        preview = escape(
            response[:220]
        )

        if len(response) > 220:
            preview += "..."

        st.html(
            f"""
            <div class="recent-card">

                <div class="recent-date">
                    📅 {reflection_date}
                </div>

                <div class="recent-prompt">
                    {prompt}
                </div>

                <div class="recent-preview">
                    {preview}
                </div>

            </div>
            """
        )

    # =====================================================
    # NOTE ABOUT FUTURE MOOD TRACKING
    # =====================================================

    st.html(
        """
        <div class="gentle-card">

            <div class="gentle-title">
                Coming next 🌱
            </div>

            <div class="gentle-text">
                A future version can let you optionally record
                your own mood before a reflection. That would
                allow Lumora to show mood trends based on data
                you explicitly choose to provide.
            </div>

        </div>
        """
    )
