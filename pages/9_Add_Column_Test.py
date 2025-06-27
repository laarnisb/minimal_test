import streamlit as st
from database import add_user_email_column

st.set_page_config(page_title="Test Add Column", page_icon="🧪")

st.title("🧪 Test Add user_email Column")

if st.button("Run Column Addition"):
    try:
        add_user_email_column()
        st.success("✅ Column check and add completed successfully.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
