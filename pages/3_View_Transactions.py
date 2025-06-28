import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.title("📄 View Transactions")

st.write("Enter your email to view your transactions")
email = st.text_input("")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT t.id, t.amount, t.category, t.date, t.user_id, t.user_email
                    FROM transactions t
                    JOIN users u ON t.user_id = u.id
                    WHERE u.email = :email
                    ORDER BY t.date DESC
                """),
                {"email": email}
            )
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if df.empty:
            st.info("ℹ️ No transactions found for this email.")
        else:
            st.dataframe(df)

    except Exception as e:
        st.error("❌ Unable to fetch transactions. Please double-check your email or try again later.")
