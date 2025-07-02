import streamlit as st
from database import get_engine
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Budget Insights", page_icon="📊")
st.title("📊 Budget Insights")

engine = get_engine()

# Prompt for email
st.write("Enter your registered email to view your categorized spending breakdown.")
email = st.text_input("Email")

# Define category mapping
category_map = {
    "groceries": "Needs",
    "rent": "Needs",
    "utilities": "Needs",
    "transport": "Needs",
    "insurance": "Needs",
    "healthcare": "Needs",
    "internet": "Needs",
    "dining": "Wants",
    "entertainment": "Wants",
    "travel": "Wants",
    "shopping": "Wants",
    "subscriptions": "Wants",
    "savings": "Savings",
    "investment": "Savings",
    "emergency fund": "Savings",
    "retirement": "Savings"
}

def fetch_transactions(user_email):
    if not user_email:
        return pd.DataFrame()
    
    query = """
        SELECT t.amount, t.category
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE u.email = %(email)s
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"email": user_email})
    return df

try:
    df = fetch_transactions(email)

    if email and df.empty:
        st.info("No transactions found for the given email.")
    elif not email:
        st.warning("Please enter your email to view your insights.")
    else:
        # Normalize and map categories
        df["category_normalized"] = df["category"].str.lower().str.strip()
        df["broad_category"] = df["category_normalized"].map(category_map).fillna("Other")

        # Group by mapped category
        summary = df.groupby("broad_category")["amount"].sum().reset_index()

        st.subheader("Spending Summary by Needs, Wants, and Savings")
        st.dataframe(summary)

        fig = px.pie(summary, names="broad_category", values="amount", title="Spending by Category Group")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading insights: {e}")
