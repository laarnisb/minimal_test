import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
import plotly.express as px

st.set_page_config(page_title="Budget Summary Reports", page_icon="📈")
st.title("📈 Budget Summary Reports")

st.write("Enter your registered email to view your categorized spending summary.")

email = st.text_input("Email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Step 1: Get user_id
            user_query = text("SELECT id FROM users WHERE email = :email")
            user_result = conn.execute(user_query, {"email": email}).fetchone()

            if user_result:
                user_id = user_result[0]

                # Step 2: Fetch transactions
                txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                txn_result = conn.execute(txn_query, {"user_id": user_id})
                txn_df = pd.DataFrame(txn_result.fetchall(), columns=["category", "amount"])

                if not txn_df.empty:
                    # Step 3: Map categories to broad groups
                    category_mapping = {
                        "Groceries": "Needs", "Rent": "Needs", "Utilities": "Needs", "Transportation": "Needs",
                        "Dining": "Wants", "Entertainment": "Wants", "Shopping": "Wants",
                        "Savings": "Savings", "Investments": "Savings"
                    }
                    txn_df["Group"] = txn_df["category"].map(category_mapping).fillna("Other")

                    # Step 4: Group and summarize
                    summary = txn_df.groupby("Group")["amount"].sum().reset_index().rename(columns={"amount": "Total Spent"})

                    # Step 5: Display summary table
                    st.subheader("💼 Spending by Category Group")
                    st.dataframe(summary)

                    # Step 6: Show bar chart
                    fig = px.bar(summary, x="Group", y="Total Spent", color="Group",
                                 title="Spending Distribution", text_auto=True)
                    st.plotly_chart(fig)

                    st.caption("Note: 'Other' includes spending not mapped to Needs, Wants, or Savings.")
                else:
                    st.info("ℹ️ No transactions found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Failed to generate summary report: {e}")
