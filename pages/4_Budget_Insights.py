import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# Database connection setup
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Category mapping: raw category → grouped budget category
category_mapping = {
    'Groceries': 'Needs',
    'Rent': 'Needs',
    'Utilities': 'Needs',
    'Healthcare': 'Needs',
    'Transport': 'Wants',
    'Dining': 'Wants',
    'Entertainment': 'Wants',
    'Shopping': 'Wants',
    'Other': 'Wants',
    'Savings': 'Savings'
}

# Streamlit page config
st.set_page_config(page_title="Budget Insights", page_icon="📊")

st.title("📊 Budget Insights")
st.markdown("Get a breakdown of your actual spending grouped into **Needs**, **Wants**, and **Savings**.")

# Email input
email = st.text_input("Enter your registered email")

if email:
    with engine.connect() as conn:
        query = """
            SELECT t.category, t.amount
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE u.email = %(email)s
        """
        transactions_df = pd.read_sql(query, conn, params={"email": email})

    if transactions_df.empty:
        st.warning("No transactions found for this user.")
    else:
        # Map to broader budget categories
        transactions_df["budget_category"] = transactions_df["category"].map(category_mapping).fillna("Other")

        summary = (
            transactions_df.groupby("budget_category")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"budget_category": "Category", "amount": "Total Amount"})
        )

        st.subheader("🧾 Spending Summary")
        st.dataframe(summary)

        # Pie Chart
        st.subheader("📌 Spending by Category")
        fig1, ax1 = plt.subplots()
        ax1.pie(
            summary["Total Amount"],
            labels=summary["Category"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax1.axis("equal")
        st.pyplot(fig1)

        # Bar Chart
        st.subheader("📊 Spending Breakdown")
        fig2, ax2 = plt.subplots()
        ax2.bar(summary["Category"], summary["Total Amount"])
        ax2.set_xlabel("Category")
        ax2.set_ylabel("Amount ($)")
        ax2.set_title("Actual Spending by Category")
        st.pyplot(fig2)

        # Download CSV
        csv = summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Summary as CSV",
            data=csv,
            file_name="budget_insights_summary.csv",
            mime="text/csv"
        )
