import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Financial Tips", page_icon="💡")
st.title("💡 Financial Tips and Recommendations")

st.write("Enter your registered email to receive tailored financial advice based on your spending.")

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
                goals_query = text("SELECT income, needs_percent, wants_percent, savings_percent FROM budget_goals WHERE user_id = :user_id")
                goals_result = conn.execute(goals_query, {"user_id": user_id}).fetchone()

                # Step 3: Get transactions
                txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                txn_df = pd.read_sql(txn_query, conn, params={"user_id": user_id})

                if goals_result and not txn_df.empty:
                    income, needs_pct, wants_pct, savings_pct = goals_result
                    category_mapping = {
                        "groceries": "Needs", "rent": "Needs", "utilities": "Needs", "transport": "Needs",
                        "insurance": "Needs", "healthcare": "Needs", "internet": "Needs",
                        "dining": "Wants", "entertainment": "Wants", "travel": "Wants", "shopping": "Wants",
                        "subscriptions": "Wants", "savings": "Savings", "investment": "Savings",
                        "emergency fund": "Savings", "retirement": "Savings"
                    }
                    txn_df["group"] = txn_df["category"].str.lower().map(category_mapping).fillna("Other")

                    # Aggregate spending
                    actual_spending = txn_df.groupby("group")["amount"].sum().to_dict()
                    for key in ["Needs", "Wants", "Savings"]:
                        actual_spending.setdefault(key, 0)

                    # Calculate actual percentages
                    total_spent = sum(actual_spending.values())
                    actual_pct = {k: round((v / income) * 100, 2) for k, v in actual_spending.items()}

                    st.subheader("📊 Spending vs. 50/30/20 Rule")
                    st.write("Your actual spending compared to the ideal budget distribution:")

                    comparison_df = pd.DataFrame({
                        "Ideal %": {"Needs": needs_pct, "Wants": wants_pct, "Savings": savings_pct},
                        "Your %": actual_pct
                    })
                    st.dataframe(comparison_df)

                    # Step 4: Generate Tips
                    st.subheader("📝 Recommendations")
                    if actual_pct["Needs"] > needs_pct:
                        st.warning("You're spending more than 50% on needs. Consider reducing rent, groceries, or utility expenses.")
                    else:
                        st.success("Your spending on needs is within the ideal range.")

                    if actual_pct["Wants"] > wants_pct:
                        st.warning("You're spending more than 30% on wants. You may want to limit discretionary purchases like entertainment or dining.")
                    else:
                        st.success("You're managing your wants spending well!")

                    if actual_pct["Savings"] < savings_pct:
                        st.error("You're saving less than 20%. Consider automating your savings or setting up an emergency fund.")
                    else:
                        st.success("Great job! You're meeting your savings goal.")

                elif txn_df.empty:
                    st.info("ℹ️ No transactions found for this user.")
                else:
                    st.warning("⚠️ No budget goals found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Failed to load recommendations: {e}")
