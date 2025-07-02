import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text
from database import get_engine
import io
import xlsxwriter

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")
st.write("Enter your registered email to view a summary of your spending vs. your budget goals.")

email = st.text_input("Email")

if email:
    engine = get_engine()

    with engine.begin() as conn:
        # Get user_id
        user_id_result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
        if not user_id_result:
            st.error("❌ No user found with this email.")
        else:
            user_id = user_id_result[0]

            # Get transaction totals by category
            transactions_query = text("""
                SELECT category, SUM(amount) AS total
                FROM transactions
                WHERE user_id = :user_id
                GROUP BY category
            """)
            transactions = pd.read_sql(transactions_query, conn, params={"user_id": user_id})

            # Get budget goals
            goals_query = text("""
                SELECT income, needs_percent, wants_percent, savings_percent
                FROM budget_goals
                WHERE user_id = :user_id
            """)
            goals = conn.execute(goals_query, {"user_id": user_id}).fetchone()

            if goals:
                income, needs_pct, wants_pct, savings_pct = goals
                budget = {
                    "Needs": income * needs_pct / 100,
                    "Wants": income * wants_pct / 100,
                    "Savings": income * savings_pct / 100
                }

                # Create summary table
                summary_df = pd.DataFrame({
                    "Category": ["Needs", "Wants", "Savings"],
                    "Actual Spending": [
                        transactions.loc[transactions["category"] == "Needs", "total"].sum(),
                        transactions.loc[transactions["category"] == "Wants", "total"].sum(),
                        transactions.loc[transactions["category"] == "Savings", "total"].sum()
                    ],
                    "Goal Amount": [budget["Needs"], budget["Wants"], budget["Savings"]]
                })

                # Display summary
                st.subheader("📈 Budget Summary")
                st.dataframe(summary_df)

                # Bar Chart
                st.subheader("📊 Comparison Chart")
                fig, ax = plt.subplots()
                summary_df.set_index("Category")[["Actual Spending", "Goal Amount"]].plot(kind='bar', ax=ax)
                plt.ylabel("Amount ($)")
                plt.title("Actual Spending vs. Budget Goals")
                st.pyplot(fig)

                # CSV Download
                csv_data = summary_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name="budget_summary.csv",
                    mime="text/csv"
                )

                # Excel Download
                try:
                    summary_df.columns = ['Category', 'Actual Spending', 'Goal Amount']  # Rename columns cleanly
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        summary_df.to_excel(writer, index=False, sheet_name='Summary')
                        writer.save()
                    st.download_button(
                        label="📥 Download Summary as Excel",
                        data=output.getvalue(),
                        file_name="budget_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"❌ Error generating Excel summary: {e}")
            else:
                st.warning("⚠️ Budget goals not found for this user.")
