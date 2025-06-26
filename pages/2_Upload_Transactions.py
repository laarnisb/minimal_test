import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Upload Transactions", page_icon="📤")

st.title("📤 Upload and Save Your Transactions")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write("Preview of uploaded data:")
    st.dataframe(df)

    # Optional: Validate columns
    expected_columns = {'date', 'amount', 'category', 'description'}
    if not expected_columns.issubset(df.columns):
        st.error(f"CSV must contain these columns: {expected_columns}")
    else:
        # Optional: Add user_id column if needed
        df['user_id'] = 1  # For now, hardcoded (replace with real user_id from session)

        if st.button("Save to Database"):
            engine = get_engine()
            with engine.begin() as conn:
                for _, row in df.iterrows():
                    insert_stmt = text("""
                        INSERT INTO transactions (user_id, date, amount, category, description)
                        VALUES (:user_id, :date, :amount, :category, :description)
                    """)
                    conn.execute(insert_stmt, {
                        'user_id': row['user_id'],
                        'date': row['date'],
                        'amount': row['amount'],
                        'category': row['category'],
                        'description': row['description']
                    })

            st.success("✅ Transactions saved to database!")
