import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
import plotly.express as px
import io

st.set_page_config(page_title="Budget Summary Reports", page_icon="📑")
st.title("📑 Budget Summary Reports")
st.write("Enter your registered email to view a summary of your spending vs. your budget goals.")

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

                # Step 2: Get budget goals
                goals_query = text("""
                    SELECT income, needs_percent, wants_percent, savings_percent
                    FROM budget_goals WHERE user_id = :user_id
                """)
                goals_result = conn.execute(goals_query, {"user_id": user_id}).fetchone()

                if goals_result:
                    income, needs_pct, wants_pct, savings_pct = goals_result
                    budget = {
                        "Needs": round(income * needs_pct / 100, 2),
                        "Wants": round(income * wants_pct / 100, 2),
                        "Savings": round(income * savings_pct / 100, 2)
                    }

                    # Step 3: Get user's transactions
                    txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                    txn_df = pd.read_sql(txn_query, conn, params={"user_id": user_id})

                    if not txn_df.empty:
                        # Step 4: Categorize transactions
                        category_mapping = {
                            "Groceries": "Needs", "Rent": "Needs", "Utilities": "Needs", "Transportation": "Needs",
                            "Dining": "Wants", "Entertainment": "Wants", "Shopping": "Wants",
                            "Savings": "Savings", "Investments": "Savings"
                        }
                        txn_df["Group"] = txn_df["category"].map(category_mapping).fillna("Other")

                        # Step 5: Summarize spending
                        summary_df = txn_df.groupby("Group")["amount"].sum().reset_index()
                        summary_df.columns = ["Category", "Total Spent"]
                        summary_df = summary_df.sort_values(by="Category")

                        # Step 6: Build comparison DataFrame
                        comparison_data = {"Category": [], "Actual": [], "Goal": []}
                        for group in ["Needs", "Wants", "Savings"]:
                            actual = summary_df[summary_df["Category"] == group]["Total Spent"].sum()
                            comparison_data["Category"].append(group)
                            comparison_data["Actual"].append(actual)
                            comparison_data["Goal"].append(budget.get(group, 0))

                        comparison_df = pd.DataFrame(comparison_data)

                        # Step 7: Bar chart
                        st.subheader("📊 Comparison Chart")
                        fig = px.bar(comparison_df, x="Category", y=["Actual", "Goal"],
                                     barmode="group", title="Actual Spending vs. Budget Goals",
                                     labels={"value": "Amount ($)", "variable": "Legend"})
                        st.plotly_chart(fig)

                        # Step 8: Pie chart
                        st.subheader("🧁 Spending Distribution")
                        fig2 = px.pie(summary_df, names="Category", values="Total Spent",
                                      title="Spending by Category")
                        st.plotly_chart(fig2)

                        # Step 9: Export to Excel
                        st.subheader("📥 Export Report")
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            summary_df.to_excel(writer, index=False, sheet_name="Summary")
                            comparison_df.to_excel(writer, index=False, sheet_name="Comparison")
                        output.seek(0)

                        st.download_button(
                            label="📥 Download Report as Excel",
                            data=output,
                            file_name="budget_summary.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Optional: show table
                        st.subheader("🧾 Detailed Spending Summary")
                        st.dataframe(summary_df)

                    else:
                        st.info("ℹ️ No transactions found for this user.")
                else:
                    st.warning("⚠️ No budget goals found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Error generating summary: {e}")
