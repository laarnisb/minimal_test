import streamlit as st
from database import engine

st.set_page_config(page_title="Minimal Test App", layout="centered")
st.title("🔌 Database Connection Test")

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT NOW()").fetchone()
        st.success(f"Connected! Server time: {result[0]}")
except Exception as e:
    st.error(f"Connection failed: {e}")
