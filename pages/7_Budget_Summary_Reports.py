import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
import plotly.express as px

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")

st.write("Enter your registered email to generate your personalized budget summary.")

email = st.text_input("Email")

# Define category mapping
category_mapping = {
    "rent": "Needs",
    "groceries": "Needs",
    "transport": "Needs",
    "utilities": "Needs",
    "insurance": "Needs",
    "phone": "Needs",
    "internet": "Needs",

    "entertainment": "Wants",
    "netflix": "Wants",
    "concert": "Wants",
    "travel": "Wants",
    "shopping": "Wants",
    "eating out": "Wants",

    "savings": "Savings",
    "investment": "Savings",
    "401k contribution": "Savings",
    "emergency fund": "Savings",
}

def classify_category(desc):
    desc = desc.lower()
    for keyword, group in category_mapping.items():
        if keyword in desc:
            return group
    return "Uncategorized"

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Get user_id
            user_result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

            if not user_result:
                st.warning("⚠️ No user found with that email.")
            else:
                user_id = user_result[0]

                # Fetch budget goals
                goal_result = conn.execute(
                    text("""
                        SELECT income, needs_percent, wants_percent, savings_percent
                        FROM budget_goals
                        WHERE user_id = :user_id
                    """),
                    {"user_id": user_id}
                ).fetchone()

                if not goal_result:
                    st.warning("⚠️ No budget goals found. Please set them first.")
                else:
                    income, needs_pct, wants_pct, savings_pct = goal_result
                    budget_df = pd.DataFrame({
                        "Category": ["Needs", "Wants", "Savings"],
                        "Budgeted Amount": [
                            income * needs_pct / 100,
                            income * wants_pct / 100,
                            income * savings_pct / 100
                        ]
                    })

                    # Fetch user transactions
                    txn_result = conn.execute(
                        text("""
                            SELECT amount, description
                            FROM transactions
                            WHERE user_id = :user_id
                        """),
                        {"user_id": user_id}
                    )
                    transactions = txn_result.fetchall()

                    if not transactions:
                        st.info("ℹ️ No transactions found.")
                    else:
                        df_txn = pd.DataFrame(transactions, columns=["Amount", "Description"])
                        df_txn["Category"] = df_txn["Description"].apply(classify_category)

                        # Summarize actual spending by category
                        actual_summary = df_txn[df_txn["Category"] != "Uncategorized"].groupby("Category")["Amount"].sum().reset_index()
                        actual_summary.rename(columns={"Amount": "Actual Spending"}, inplace=True)

                        # Merge with budget
                        summary = pd.merge(budget_df, actual_summary, on="Category", how="left").fillna(0)

                        st.subheader("📋 Budget Summary Table")
                        st.dataframe(summary)

                        st.subheader("📊 Budget vs. Actual")
                        fig = px.bar(summary.melt(id_vars="Category", value_vars=["Budgeted Amount", "Actual Spending"]),
                                     x="Category", y="value", color="variable", barmode="group",
                                     labels={"value": "Amount ($)", "variable": "Type"},
                                     title="Budget vs. Actual Spending")
                        st.plotly_chart(fig, use_container_width=True)

                        # Export to Excel
                        output = summary.copy()
                        output["Difference"] = output["Budgeted Amount"] - output["Actual Spending"]
                        excel_file = "budget_summary.xlsx"
                        output.to_excel(excel_file, index=False)

                        with open(excel_file, "rb") as f:
                            st.download_button("📥 Download Budget Summary Report (Excel)",
                                               f,
                                               file_name=excel_file,
                                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"❌ Error: {e}")
