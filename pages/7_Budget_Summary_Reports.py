import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text
from database import get_engine
import io

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")
st.write("Enter your registered email to view a summary of your spending vs. your budget goals.")

email = st.text_input("Email")

if email:
    engine = get_engine()
    with engine.begin() as conn:
        user_id_result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()

        if not user_id_result:
            st.error("❌ Email not found in database.")
        else:
            user_id = user_id_result[0]

            transactions = pd.read_sql(
                text("SELECT amount, category FROM transactions WHERE user_id = :user_id"),
                conn, params={"user_id": user_id}
            )

            budget_result = conn.execute(
                text("""
                    SELECT income, needs_percent, wants_percent, savings_percent
                    FROM budget_goals
                    WHERE user_id = :user_id
                """), {"user_id": user_id}
            ).fetchone()

            if budget_result:
                income, needs_pct, wants_pct, savings_pct = budget_result

                actual_spending = transactions.groupby("category")["amount"].sum().reset_index()

                budget_targets = pd.DataFrame({
                    "category": ["Needs", "Wants", "Savings"],
                    "goal_amount": [income * needs_pct / 100,
                                    income * wants_pct / 100,
                                    income * savings_pct / 100]
                })

                summary_df = pd.merge(actual_spending, budget_targets, on="category", how="outer").fillna(0)
                summary_df.rename(columns={"amount": "actual_amount"}, inplace=True)

                st.subheader("📈 Budget Summary")
                st.dataframe(summary_df)

                # Bar chart
                st.subheader("📊 Comparison Chart")
                fig, ax = plt.subplots()
                bar_width = 0.35
                index = range(len(summary_df))

                ax.bar(index, summary_df["actual_amount"], bar_width, label="Actual Spending")
                ax.bar([i + bar_width for i in index], summary_df["goal_amount"], bar_width, label="Goal")

                ax.set_xlabel("Category")
                ax.set_ylabel("Amount ($)")
                ax.set_title("Actual Spending vs. Budget Goals")
                ax.set_xticks([i + bar_width / 2 for i in index])
                ax.set_xticklabels(summary_df["category"])
                ax.legend()

                st.pyplot(fig)

                # Pie chart
                st.subheader("🧁 Spending Distribution")
                if summary_df["actual_amount"].sum() > 0:
                    fig2, ax2 = plt.subplots()
                    ax2.pie(summary_df["actual_amount"], labels=summary_df["category"], autopct='%1.1f%%', startangle=90)
                    ax2.axis('equal')
                    st.pyplot(fig2)
                else:
                    st.info("No spending data available to plot.")

                # Export to CSV
                csv_data = summary_df.to_csv(index=False).encode("utf-8")
                st.download_button("📄 Download as CSV", data=csv_data, file_name="budget_summary.csv", mime="text/csv")

                # Export to Excel
                try:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        summary_df.to_excel(writer, index=False, sheet_name="Summary")

                    st.download_button(
                        "📊 Download as Excel",
                        data=excel_buffer.getvalue(),
                        file_name="budget_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"❌ Error generating Excel summary: {e}")
            else:
                st.warning("⚠️ No budget goals found for this user.")
