import streamlit as st
import pandas as pd
from database import insert_transactions
from datetime import datetime

st.set_page_config(page_title="Upload Transactions", page_icon="📤")

st.title("📤 Upload Transactions")

st.write("Please upload a CSV file with the following columns:")
st.code("user_email, amount, category, description, date")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = {"user_email", "amount", "category", "description", "date"}
        if not required_columns.issubset(df.columns):
            st.error(f"❌ Missing required columns. Required: {required_columns}")
        else:
            # Convert 'date' column to datetime format
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            if df["date"].isnull().any():
                st.warning("⚠️ Some dates couldn't be parsed and will be skipped.")

            # Rename for consistency with DB schema
            df.rename(columns={"date": "created_at"}, inplace=True)

            st.dataframe(df)

            if st.button("Submit Transactions"):
                try:
                    insert_transactions(df)
                    st.success("🎉 Transactions uploaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to upload transactions: {e}")
    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
