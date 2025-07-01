from pathlib import Path

# Re-define the content since the code execution environment was reset
budget_goals_code = '''
import streamlit as st
from sqlalchemy import text
from database import get_engine
import datetime

st.set_page_config(page_title="Set Budget Goals", page_icon="🎯")
st.title("🎯 Set Monthly Budget Goals")

st.write("Enter your monthly income and set your budget goals for Needs, Wants, and Savings.")

# Collect user input
email = st.text_input("Your registered email")
income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
needs_pct = st.slider("Needs (%)", 0, 100, 50)
wants_pct = st.slider("Wants (%)", 0, 100, 30)
savings_pct = st.slider("Savings (%)", 0, 100, 20)

# Ensure percentages add up to 100
if needs_pct + wants_pct + savings_pct != 100:
    st.warning("⚠️ The total percentage must equal 100%.")
else:
    if st.button("Save Budget Goals"):
        try:
            engine = get_engine()
            with engine.begin() as conn:
                # Lookup user_id
                user_query = text("SELECT id FROM users WHERE email = :email")
                result = conn.execute(user_query, {"email": email}).fetchone()

                if result:
                    user_id = result[0]
                    insert_query = text(\"""
                        INSERT INTO budget_goals (user_id, income, needs_percent, wants_percent, savings_percent, created_at)
                        VALUES (:user_id, :income, :needs, :wants, :savings, :created_at)
                        ON CONFLICT (user_id) DO UPDATE
                        SET income = EXCLUDED.income,
                            needs_percent = EXCLUDED.needs_percent,
                            wants_percent = EXCLUDED.wants_percent,
                            savings_percent = EXCLUDED.savings_percent,
                            created_at = EXCLUDED.created_at
                    \""")
                    conn.execute(insert_query, {
                        "user_id": user_id,
                        "income": income,
                        "needs": needs_pct,
                        "wants": wants_pct,
                        "savings": savings_pct,
                        "created_at": datetime.datetime.utcnow()
                    })
                    st.success("✅ Budget goals saved successfully!")
                else:
                    st.error("❌ Email not found in users table. Please register first.")
        except Exception as e:
            st.error(f"❌ Failed to save budget goals: {e}")
'''

# Write the file to the 'pages' directory
path = Path("pages/5_Set_Budget_Goals.py")
path.write_text(budget_goals_code.strip())

"✅ 5_Set_Budget_Goals.py has been created."
