import streamlit as st
import pandas as pd
from database import get_engine

st.set_page_config(page_title="View Transactions", page_icon="📄")

st.title("📄 View Transactions")

# Ask user for email to filter records
email = st.text_input("Enter your email to view your transactions")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = """
                SELECT * FROM transactions
                WHERE email = :email
                ORDER BY transaction_date DESC
            """
            df = pd.read_sql(query, conn, params={"email": email})

        if df.empty:
            st.info("No transactions found for this email.")
        else:
            st.success(f"Found {len(df)} transactions for {email}")
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
else:
    st.warning("Please enter your email to view transactions.")
