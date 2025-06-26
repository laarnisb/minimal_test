import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="View Transactions", page_icon="📊")
st.title("📊 View Transactions")

engine = get_engine()

# Step 1: Fetch registered users
with engine.connect() as conn:
    users = conn.execute(text("SELECT id, name FROM users")).fetchall()
user_dict = {user.name: str(user.id) for user in users}

selected_user = st.selectbox("Select user to view transactions", options=list(user_dict.keys()))
user_id = user_dict[selected_user] if selected_user else None

# Step 2: Fetch transactions
if user_id:
    with engine.connect() as conn:
        query = text("""
            SELECT date, amount, category, description
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY date DESC
        """)
        df = pd.read_sql(query, conn, params={"user_id": user_id})

    if df.empty:
        st.warning("No transactions found for this user.")
    else:
        st.subheader("Transaction Table")
        st.dataframe(df)

        # Step 3: Summary
        st.subheader("Summary")

        total = df["amount"].sum()
        by_category = df.groupby("category")["amount"].sum().reset_index()

        st.metric("Total Spending", f"${total:,.2f}")

        st.bar_chart(by_category.set_index("category"))
