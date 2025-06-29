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
            # Step 1: Get user_id from the users table using the email
            user_query = text("SELECT id FROM users WHERE email = :email")
            user_result = conn.execute(user_query, {"email": email})
            user_row = user_result.fetchone()

            if user_row:
                user_id = user_row[0]

                # Step 2: Get transactions for the corresponding user_id
                txn_query = text("""
                    SELECT amount, category, name, date 
                    FROM transactions 
                    WHERE user_id = :user_id 
                    ORDER BY date DESC
                """)
                txn_result = conn.execute(txn_query, {"user_id": user_id})
                transactions = txn_result.fetchall()

                if transactions:
                    df = pd.DataFrame(transactions, columns=["Amount", "Category", "Description", "Date"])
                    st.dataframe(df)
                else:
                    st.info("ℹ️ No transactions found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error("❌ Unable to fetch transactions. Please double-check your email or try again later.")
        st.stop()
