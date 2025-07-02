from pathlib import Path

# Recreate the file after code execution state reset
track_budget_progress_code = '''
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
import plotly.graph_objects as go

st.set_page_config(page_title="Track Budget Progress", page_icon="📊")
st.title("📊 Track Budget Progress")

st.write("Enter your registered email to compare actual spending with your budget goals.")

email = st.text_input("Email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Step 1: Fetch user_id
            user_query = text("SELECT id FROM users WHERE email = :email")
            user_result = conn.execute(user_query, {"email": email}).fetchone()

            if user_result:
                user_id = user_result[0]

                # Step 2: Fetch budget goals
                goals_query = text("SELECT income, needs_percent, wants_percent, savings_percent FROM budget_goals WHERE user_id = :user_id")
                goals_result = conn.execute(goals_query, {"user_id": user_id}).fetchone()

                if goals_result:
                    income, needs_pct, wants_pct, savings_pct = goals_result
                    budget = {
                        "Needs": round(income * needs_pct / 100, 2),
                        "Wants": round(income * wants_pct / 100, 2),
                        "Savings": round(income * savings_pct / 100, 2)
                    }

                    # Step 3: Fetch transactions
                    txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                    txn_result = conn.execute(txn_query, {"user_id": user_id})
                    txn_df = pd.DataFrame(txn_result.fetchall(), columns=["category", "amount"])

                    if not txn_df.empty:
                        # Step 4: Map categories to Needs/Wants/Savings
                        category_mapping = {
                            "groceries": "Needs", "rent": "Needs", "utilities": "Needs", "transport": "Needs",
                            "insurance": "Needs", "healthcare": "Needs", "internet": "Needs",
                            "dining": "Wants", "entertainment": "Wants", "travel": "Wants", "shopping": "Wants",
                            "subscriptions": "Wants", "savings": "Savings", "investment": "Savings",
                            "emergency fund": "Savings", "retirement": "Savings"
                        }
                        txn_df["group"] = txn_df["category"].map(category_mapping).fillna("Other")

                        # Step 5: Sum amounts per group
                        actual = txn_df.groupby("group")["amount"].sum().to_dict()
                        for key in ["Needs", "Wants", "Savings"]:
                            actual.setdefault(key, 0)

                        # Step 6: Display comparison
                        comparison_df = pd.DataFrame({
                            "Budgeted": pd.Series(budget),
                            "Actual": pd.Series(actual)
                        })
                        comparison_df["Difference"] = comparison_df["Actual"] - comparison_df["Budgeted"]
                        st.subheader("💰 Budget vs. Actual")
                        st.dataframe(comparison_df)

                        # Step 7: Bar chart
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=list(budget.keys()), y=list(budget.values()), name="Budgeted"))
                        fig.add_trace(go.Bar(x=list(actual.keys()), y=list(actual.values()), name="Actual"))
                        fig.update_layout(barmode='group', title="Spending Comparison", yaxis_title="Amount ($)")
                        st.plotly_chart(fig)
                    else:
                        st.info("ℹ️ No transactions found for this user.")
                else:
                    st.warning("⚠️ No budget goals found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Failed to track budget progress: {e}")
'''

file_path = Path("pages/6_Track_Budget_Progress.py")
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.write_text(track_budget_progress_code)

file_path.name
