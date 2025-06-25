import streamlit as st
from database import test_connection

st.set_page_config(page_title="Database Test", layout="centered")

st.title("✅ Database Connection Test")

if st.button("Test Connection"):
    try:
        timestamp = test_connection()
        st.success(f"Connection successful! Server time: {timestamp}")
    except Exception as e:
        st.error(f"Connection failed: {e}")