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
            # Step 1: Find user_id by email
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user_email})
            user_row = result.fetchone()

            if user_row:
                user_id = user_row[0]

                # Step 2: Fetch transactions by user_id
                tx_result = conn.execute(
                    text("SELECT * FROM transactions WHERE user_id = :user_id ORDER BY date DESC"),
                    {"user_id": user_id}
                )
                df = pd.DataFrame(tx_result.fetchall(), columns=tx_result.keys())

                if df.empty:
                    st.warning("No transactions found for this user.")
                else:
                    st.dataframe(df)
            else:
                st.error("Email not found. Please register first.")

    except Exception as e:
        st.error("❌ Unable to fetch transactions. Please double-check your email or try again later.")
