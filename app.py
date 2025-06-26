import streamlit as st

st.set_page_config(page_title="WiseBudget", page_icon="💰", layout="centered")

st.title("💰 Welcome to WiseBudget")
st.markdown(
    """
    **WiseBudget** helps you track and manage your finances with ease.

    Use the sidebar to:
    - 📝 Register users
    - 📊 Upload and analyze your spending data
    - 📈 View financial insights and trends
    """
)

st.info("👉 Select a page from the sidebar to begin.")
