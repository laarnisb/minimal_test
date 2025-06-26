import streamlit as st
from database import insert_user
from datetime import datetime

st.set_page_config(page_title="Register User", page_icon="📝")

st.title("📝 Register a New User")

with st.form("registration_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    submitted = st.form_submit_button("Register")

    if submitted:
        if name and email:
            try:
                insert_user(name, email, datetime.utcnow())
                st.success("🎉 User registered successfully!")
            except Exception as e:
                st.error(f"❌ Failed to register user: {e}")
        else:
            st.warning("Please enter both name and email.")
