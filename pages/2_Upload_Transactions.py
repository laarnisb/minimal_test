import streamlit as st
import pandas as pd
from database import insert_transactions

st.set_page_config(page_title="Upload Transactions", page_icon="📤")

st.title("📤 Upload Transactions")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Show preview of data
        st.write("### Preview:")
        st.dataframe(df)

        # Rename 'created_at' to 'date' if necessary
        if 'created_at' in df.columns and 'date' not in df.columns:
            df.rename(columns={'created_at': 'date'}, inplace=True)

        # Validate required columns
        required_columns = {"user_email", "amount", "category", "description", "date"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            st.error(f"Missing required columns: {', '.join(missing)}")
        else:
            # Parse 'date' column to datetime
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

            if df["date"].isnull().any():
                st.warning("Some dates could not be parsed and were set to NaT.")

            if st.button("Submit Transactions"):
                try:
                    insert_transactions(df)
                    st.success("✅ Transactions uploaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to upload transactions: {e}")

    except Exception as e:
        st.error(f"❌ Failed to read the file: {e}")
else:
    st.info("Please upload a CSV file to proceed.")

from database import get_engine
from sqlalchemy import text

engine = get_engine()

def check_transactions_columns():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'transactions'
        """))
        return [row[0] for row in result.fetchall()]

# Debug output
st.subheader("🧪 Debug: Transactions Table Columns")
st.write(check_transactions_columns())
