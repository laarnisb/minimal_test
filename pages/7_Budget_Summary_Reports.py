import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")

st.write("Enter your registered email to view a summary of your spending vs. your budget goals.")

email = st.text_input("Email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Get user_id
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
            if result:
                user_id = result[0]

                # Get budget goals
                budget_query = text("""
                    SELECT income, needs_percent, wants_percent, savings_percent
                    FROM budget_goals
                    WHERE user_id = :user_id
                """)
                budget = conn.execute(budget_query, {"user_id": user_id}).fetchone()

                if budget:
                    income, needs_pct, wants_pct, savings_pct = budget

                    # Get actual transactions
                    tx_query = text("""
                        SELECT category, SUM(amount) as total
                        FROM transactions
                        WHERE user_id = :user_id
                        GROUP BY category
                    """)
                    tx_df = pd.read_sql(tx_query, conn, params={"user_id": user_id})

                    # Categorize actuals into needs/wants/savings
                    def classify(cat):
                        cat = cat.lower()
                        if cat in ["groceries", "utilities", "rent", "mortgage", "insurance"]:
                            return "Needs"
                        elif cat in ["entertainment", "eating out", "shopping", "travel"]:
                            return "Wants"
                        elif cat in ["savings", "investments", "emergency fund"]:
                            return "Savings"
                        else:
                            return "Other"

                    tx_df["CategoryType"] = tx_df["category"].apply(classify)
                    summary_df = tx_df.groupby("CategoryType")["total"].sum().reset_index()

                    # Append goal values for comparison
                    summary_df = summary_df[summary_df["CategoryType"].isin(["Needs", "Wants", "Savings"])]
                    summary_df["Goal Amount"] = summary_df["CategoryType"].map({
                        "Needs": income * needs_pct / 100,
                        "Wants": income * wants_pct / 100,
                        "Savings": income * savings_pct / 100
                    })

                    st.subheader("📈 Budget Summary")
                    st.dataframe(summary_df)

                    # Visualization
                    st.subheader("📊 Comparison Chart")
                    fig, ax = plt.subplots()
                    index = range(len(summary_df))
                    bar_width = 0.35
                    actuals = summary_df["Total"]
                    goals = summary_df["Goal Amount"]
                    labels = summary_df["CategoryType"]

                    ax.bar(index, actuals, bar_width, label="Actual")
                    ax.bar([i + bar_width for i in index], goals, bar_width, label="Goal")
                    ax.set_xticks([i + bar_width / 2 for i in index])
                    ax.set_xticklabels(labels)
                    ax.set_ylabel("Amount ($)")
                    ax.set_title("Actual Spending vs. Budget Goals")
                    ax.legend()
                    st.pyplot(fig)

                    # Export buttons
                    def to_excel(df):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Summary')
                        return output.getvalue()

                    if not summary_df.empty:
                        st.download_button("⬇️ Download as CSV", summary_df.to_csv(index=False), "budget_summary.csv", "text/csv")
                        st.download_button("⬇️ Download as Excel", to_excel(summary_df), "budget_summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("⚠️ No budget goals found for this user.")
            else:
                st.error("❌ Email not found.")
    except Exception as e:
        st.error(f"❌ Error generating summary: {e}")
