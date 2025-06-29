import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="View Transactions", page_icon="📄")
st.title("📄 View Transactions")

st.write("Enter your registered email to view your uploaded transactions.")

email = st.text_input("Email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Step 1: Find user_id from users table
            user_query = text("SELECT id FROM users WHERE email = :email")
            user_result = conn.execute(user_query, {"email": email})
            user_row = user_result.fetchone()

            if user_row:
                user_id = user_row[0]

                # Step 2: Fetch transactions based on user_id
                txn_query = text("""
                    SELECT amount, category, description, date
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
                    st.info("ℹ️ No transactions found for this email.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Error fetching transactions: {e}")
