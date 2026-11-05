import streamlit as st

st.title("Lumora Debug")

st.write("STEP 1: Starting...")

from app.database.db import initialize_database
st.write("STEP 2: Database imported")

from app.ui.chat import render_chat
st.write("STEP 3: Chat imported")

from app.ui.memories import render_memories
st.write("STEP 4: Memories imported")

from app.ui.calendar import render_calendar
st.write("STEP 5: Calendar imported")

from app.ui.reflection import render_reflection
st.write("STEP 6: Reflection imported")

from app.ui.search import render_search
st.write("STEP 7: Search imported")

from app.ui.mood_insights import render_mood_insights
st.write("STEP 8: Mood insights imported")

from app.ui.space import render_space
st.write("STEP 9: Space imported")

from app.ui.relationship_support import render_relationship_support
st.write("STEP 10: Relationship support imported")

st.success("ALL IMPORTS WORK!")