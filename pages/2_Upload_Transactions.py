import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Upload Transactions", page_icon="📤")
st.title("📤 Upload Transactions")

st.write("Upload a CSV file with columns: user_email, amount, category, description, date")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = {"user_email", "amount", "category", "description", "date"}
        if not required_columns.issubset(df.columns):
            st.error(f"❌ CSV must include columns: {', '.join(required_columns)}")
        else:
            engine = get_engine()
            success_count = 0

            with engine.begin() as conn:
                for _, row in df.iterrows():
                    # Lookup user_id by email
                    user_query = text("SELECT id FROM users WHERE email = :email")
                    result = conn.execute(user_query, {"email": row["user_email"]}).fetchone()

                    if result:
                        user_id = result[0]
                        insert_query = text("""
                            INSERT INTO transactions (user_id, amount, category, description, date)
                            VALUES (:user_id, :amount, :category, :description, :date)
                        """)
                        conn.execute(insert_query, {
                            "user_id": user_id,
                            "amount": row["amount"],
                            "category": row["category"],
                            "description": row["description"],
                            "date": row["date"]
                        })
                        success_count += 1
                    else:
                        st.warning(f"⚠️ Email not found in users table: {row['user_email']}")

            if success_count:
                st.success(f"✅ Successfully uploaded {success_count} transaction(s).")
            else:
                st.warning("⚠️ No transactions were uploaded. Please check your CSV file and emails.")

    except Exception as e:
        st.error(f"❌ Failed to upload transactions: {e}")
