import streamlit as st
import pandas as pd
from database import get_engine
from sqlalchemy import text

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")

email = st.text_input("Enter your registered email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Retrieve user ID
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            user = result.fetchone()

            if user:
                user_id = user[0]

                # Fetch budget goals
                goals = conn.execute(text("""
                    SELECT income, needs_percent, wants_percent, savings_percent 
                    FROM budget_goals WHERE user_id = :user_id
                """), {"user_id": user_id}).fetchone()

                # Fetch actual spending
                spending = conn.execute(text("""
                    SELECT category, SUM(amount) AS total_spent 
                    FROM transactions 
                    WHERE user_id = :user_id 
                    GROUP BY category
                """), {"user_id": user_id}).fetchall()

                if goals and spending:
                    income, needs_pct, wants_pct, savings_pct = goals
                    budget_targets = {
                        "Needs": income * needs_pct / 100,
                        "Wants": income * wants_pct / 100,
                        "Savings": income * savings_pct / 100,
                    }

                    actuals = {row[0]: row[1] for row in spending}
                    st.subheader("📈 Budget Summary")

                    summary_df = pd.DataFrame({
                        "Budgeted": budget_targets,
                        "Actual": [actuals.get(cat, 0) for cat in budget_targets]
                    })

                    st.dataframe(summary_df)

                    st.bar_chart(summary_df)
                else:
                    st.info("No data available for this user.")
            else:
                st.warning("⚠️ User not found.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
