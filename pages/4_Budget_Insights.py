import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Budget Insights", page_icon="📊")
st.title("📊 Budget Insights")

st.write("Enter your registered email to view your categorized spending breakdown.")

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

                # Step 2: Get transactions
                txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                txn_df = pd.read_sql(txn_query, conn, params={"user_id": user_id})

                if not txn_df.empty:
                    # Step 3: Map categories to budget groups
                    category_mapping = {
                        "groceries": "Needs", "rent": "Needs", "utilities": "Needs", "transport": "Needs",
                        "insurance": "Needs", "healthcare": "Needs", "internet": "Needs",
                        "dining": "Wants", "entertainment": "Wants", "travel": "Wants", "shopping": "Wants",
                        "subscriptions": "Wants", "savings": "Savings", "investment": "Savings",
                        "emergency fund": "Savings", "retirement": "Savings"
                    }
                    
                    # Normalize category names
                    txn_df["category"] = txn_df["category"].str.strip().str.lower()

                    # Map and assign group
                    txn_df["Group"] = txn_df["category"].map(category_mapping).fillna("Other")

                    # Step 4: Summarize spending by group
                    summary_df = txn_df.groupby("broad_category")["amount"].sum().reset_index()
                    summary_df.columns = ["Category Group", "Total Spending"]

                    # Step 5: Show summary table
                    st.subheader("Spending Summary by Needs, Wants, and Savings")
                    st.dataframe(summary_df)

                    # Step 6: Pie chart
                    fig = px.pie(summary_df, names="Category Group", values="Total Spending",
                                 title="Spending by Category Group")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transactions found for this user.")
            else:
                st.warning("No user found with that email.")
    except Exception as e:
        st.error(f"Error loading insights: {e}")
