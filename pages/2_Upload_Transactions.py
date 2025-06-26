import streamlit as st
from database import get_engine
from sqlalchemy import text

st.set_page_config(page_title="Test DB Engine", page_icon="🧪")
st.title("🧪 Test DB Engine")

if st.button("Run Test Query"):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).scalar()
        st.success(f"✅ Success! Server time is: {result}")
    except Exception as e:
        st.error(f"❌ Failed to connect to DB: {e}")
