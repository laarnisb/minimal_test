import streamlit as st
from database import test_connection

st.set_page_config(page_title="Database Connection Test", page_icon="🔌")

st.title("🔌 Database Connection Test")

if st.button("Test Connection"):
    try:
        server_time = test_connection()
        st.success(f"🎉 Connected! Server time: {server_time}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")    