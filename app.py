import streamlit as st
from datetime import datetime
from pathlib import Path

from app.database.db import initialize_database
from app.database.seed import seed_if_empty
from app.database.models import get_conversations, get_important_dates, get_memories

from app.ui.chat import render_chat
from app.ui.memories import render_memories
from app.ui.calendar import render_calendar
from app.ui.reflection import render_reflection
from app.ui.search import render_search
from app.ui.mood_insights import render_mood_insights
from app.ui.space import render_space
from app.ui.relationship_support import render_relationship_support

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Lumora",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto"
)


# =========================================================
# DATABASE
# =========================================================

initialize_database()
seed_if_empty()


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "pending_date_suggestions" not in st.session_state:
    st.session_state.pending_date_suggestions = []

# =========================================================
# LUMORA GLOBAL UI
# =========================================================

USER_NAME = "Harmanpreet Kaur"

_THEME_CSS = (
    Path(__file__).parent / "app" / "ui" / "theme.css"
).read_text(encoding="utf-8")

# The active sidebar item gets the "lx-active" styling.
st.html(
    "<style>"
    + _THEME_CSS.replace(
        "lx-active", f"st-key-sidebar_{st.session_state.page}"
    )
    + "</style>"
)


# Button callbacks run before the script, so a click costs one rerun, not two.
def go(page):
    st.session_state.page = page


def toggle_sidebar_pin():
    st.session_state.sidebar_pinned = not st.session_state.sidebar_pinned


# =========================================================
# SIDEBAR
# =========================================================

NAV_ITEMS = [
    ("home", "Home", ":material/home:"),
    ("chat", "Chat", ":material/forum:"),
    ("memories", "Memories", ":material/photo_library:"),
    ("calendar", "Calendar", ":material/calendar_month:"),
    ("reflection", "Reflection", ":material/self_improvement:"),
    ("search", "Search", ":material/search:"),
    ("space", "Your Space", ":material/person:"),
]

# Pinned = full sidebar. Unpinned = icon rail that expands on hover.
st.session_state.setdefault("sidebar_pinned", True)

with st.sidebar:

    with st.container(key="lx_nav"):

        pinned = st.session_state.sidebar_pinned

        st.button(
            "Auto-hide sidebar" if pinned else "Keep sidebar open",
            key="sidebar_pin",
            icon=":material/left_panel_close:" if pinned else ":material/push_pin:",
            help="Shrink to icons, expand on hover" if pinned else "Keep the sidebar open",
            on_click=toggle_sidebar_pin,
        )

        st.html(f"""
        {'' if pinned else '<div class="lx-rail-on"></div>'}
        <div class="sidebar-brand">
            <div class="sidebar-logo">🌿</div>
            <div class="sidebar-title">Lumora</div>
            <div class="sidebar-subtitle">
                {USER_NAME}'s space to feel, talk and grow
            </div>
        </div>
        <div class="sidebar-divider"></div>
        <div class="lx-nav-label">Navigate</div>
        """)

        for page, label, icon in NAV_ITEMS:
            st.button(
                label, key=f"sidebar_{page}", icon=icon,
                use_container_width=True, on_click=go, args=(page,),
            )

        st.html("""
        <div class="sidebar-quote">
            <b>A small step</b><br>
            every day still counts. 💜
        </div>
        """)


# =========================================================
# HOME PAGE
# =========================================================

def _greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def render_home():

    memories_count = len(get_memories())
    dates_count = len(get_important_dates())
    chats_count = len(get_conversations())

    # ---------------- HERO ----------------

    with st.container(key="lx_hero"):

        st.html("""
        <div class="lx-orbs">
            <div class="lx-orb o1"></div>
            <div class="lx-orb o2"></div>
            <div class="lx-orb o3"></div>
        </div>
        """)

        left, right = st.columns(
            [1.4, 1], gap="large", vertical_alignment="center"
        )

        with left:

            st.html(f"""
            <div class="lx-eyebrow">{datetime.now():%A, %d %B}</div>
            <h1 class="lx-hero-title">
                {_greeting()},
                <em>{USER_NAME}</em>
            </h1>
            <p class="lx-hero-sub">
                How are you feeling today? This is your quiet corner
                to share your thoughts, feelings, or anything that's
                on your mind.
            </p>
            """)

            with st.container(horizontal=True, gap="small"):

                st.button(
                    "Start a conversation  →",
                    key="home_start_chat",
                    type="primary",
                    on_click=go, args=("chat",),
                )

                st.button(
                    "Write a reflection", key="home_reflect",
                    on_click=go, args=("reflection",),
                )

        with right:

            st.html("""
            <div class="lx-mood">
                <div class="lx-eyebrow">Today's reflection</div>
                <div class="lx-mood-title" style="margin-top:14px">
                    How are you feeling right now?
                </div>
                <div class="lx-mood-sub">
                    Pick a feeling in your head, then tell Lumora about it.
                </div>
                <div class="lx-mood-row">
                    <span>😌</span><span>😮</span><span>😀</span>
                    <span>😊</span><span>🌸</span>
                </div>
            </div>
            """)

    # ---------------- MARQUEE ----------------

    chips = "".join(
        f'<span class="lx-chip"><i>✦</i>{c}</span>'
        for c in [
            "AI Companion", "Multilingual", "Dates & Reminders",
            "Memories", "Mood Insights", "Reflection",
            "Relationship Support", "Private & Gentle",
        ]
    )

    st.html(f"""
    <div class="lx-marquee" aria-hidden="true">
        <div class="lx-marquee-track">{chips}{chips}</div>
    </div>
    """)

    # ---------------- STATS ----------------

    st.html(f"""
    <div class="lx-stats lx-reveal">
        <div class="lx-stat">
            <div class="lx-stat-num">{chats_count}</div>
            <div class="lx-stat-label">Conversations</div>
        </div>
        <div class="lx-stat">
            <div class="lx-stat-num">{memories_count}</div>
            <div class="lx-stat-label">Saved moments</div>
        </div>
        <div class="lx-stat">
            <div class="lx-stat-num">{dates_count}</div>
            <div class="lx-stat-label">Important dates</div>
        </div>
    </div>
    """)

    # ---------------- EXPLORE ----------------

    st.html("""
    <div class="lx-section-head">
        <div>
            <div class="lx-eyebrow">Explore</div>
            <div class="lx-section-title">Your space, <em>beautifully kept</em></div>
        </div>
        <div class="lx-section-note">
            Everything you share with Lumora lives here, gently organised
            and only ever for you.
        </div>
    </div>
    """)

    cards = [
        ("memories", "📸", "Memories",
         f"{memories_count} saved moment{'s' if memories_count != 1 else ''}",
         "Open memories"),
        ("calendar", "📅", "Upcoming",
         f"{dates_count} important date{'s' if dates_count != 1 else ''}",
         "Open calendar"),
        ("mood_insights", "📊", "Mood Insights",
         "See the patterns in how you feel.",
         "Open mood insights"),
        ("relationship", "♡", "Relationship Support",
         "Guidance for tougher days.",
         "Talk to Lumora about relationships"),
    ]

    for col, (i, (page, icon, title, text, aria)) in zip(
        st.columns(4, gap="medium"), enumerate(cards, 1)
    ):
        with col:
            with st.container(key=f"lx_card_{page}"):
                st.html(f"""
                <div class="lx-card-top">
                    <span class="lx-icon">{icon}</span>
                    <span class="lx-card-index">0{i}</span>
                </div>
                <div class="lx-card-title">{title}</div>
                <div class="lx-card-text">{text}</div>
                <div class="lx-card-link">Open <b>→</b></div>
                """)
                st.button(aria, key=f"home_{page}", on_click=go, args=(page,))

    # ---------------- QUOTE + FOOTER ----------------

    st.html(f"""
    <div class="lx-quote lx-reveal">
        <div class="lx-quote-mark">“</div>
        <div class="lx-quote-text">
            A small step every day still counts.
        </div>
        <div class="lx-quote-by">For {USER_NAME}</div>
    </div>

    <div class="lx-footer">
        <span><strong>Lumora</strong> &nbsp;·&nbsp; your space to feel, talk and grow</span>
        <span>Lumora is a supportive companion, not a replacement for professional care.</span>
    </div>
    """)


# =========================================================
# PAGE ROUTING
# =========================================================

if st.session_state.page == "home":

    render_home()


elif st.session_state.page == "chat":

    render_chat()


elif st.session_state.page == "memories":

    render_memories()


elif st.session_state.page == "calendar":

    render_calendar()


elif st.session_state.page == "reflection":

    render_reflection()


elif st.session_state.page == "search":

    render_search()


elif st.session_state.page == "mood_insights":

    render_mood_insights()

elif st.session_state.page == "relationship":

    render_relationship_support() 
    
elif st.session_state.page == "space":

    render_space()