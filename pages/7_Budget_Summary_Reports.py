import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Budget Summary Reports", page_icon="📊")
st.title("📊 Budget Summary Reports")

st.write("Enter your registered email to view a summary of your spending vs. your budget goals.")

email = st.text_input("Email")

if email:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Step 1: Get user_id
            user_result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
            if not user_result:
                st.warning("⚠️ No user found with that email.")
            else:
                user_id = user_result[0]

                # Step 2: Fetch transactions
                txn_result = conn.execute(text("""
                    SELECT category, amount FROM transactions
                    WHERE user_id = :user_id
                """), {"user_id": user_id}).fetchall()

                # Step 3: Fetch budget goals
                goal_result = conn.execute(text("""
                    SELECT income, needs_percent, wants_percent, savings_percent
                    FROM budget_goals
                    WHERE user_id = :user_id
                """), {"user_id": user_id}).fetchone()

                if not txn_result:
                    st.info("ℹ️ No transactions found for this user.")
                elif not goal_result:
                    st.info("ℹ️ No budget goals set for this user.")
                else:
                    # Prepare data
                    df = pd.DataFrame(txn_result, columns=["Category", "Amount"])
                    income, needs_pct, wants_pct, savings_pct = goal_result
                    total_spent = df["Amount"].sum()

                    # Actual spending
                    category_totals = df.groupby("Category")["Amount"].sum().reset_index()

                    # Pie Chart of Spending Breakdown
                    st.subheader("🧾 Spending Breakdown")
                    fig1, ax1 = plt.subplots()
                    ax1.pie(category_totals["Amount"], labels=category_totals["Category"], autopct="%1.1f%%", startangle=90)
                    ax1.axis("equal")
                    st.pyplot(fig1)

                    # Budgeted amounts
                    st.subheader("📌 Budget Goals vs Actual Spending")
                    budget_data = pd.DataFrame({
                        "Type": ["Needs", "Wants", "Savings"],
                        "Budgeted Amount": [
                            income * needs_pct / 100,
                            income * wants_pct / 100,
                            income * savings_pct / 100
                        ]
                    })

                    # Approximate classification for demo
                    needs_keywords = ["rent", "groceries", "utilities", "insurance", "health"]
                    wants_keywords = ["entertainment", "shopping", "dining"]
                    savings_keywords = ["savings", "investment", "retirement"]

                    def classify(row):
                        category = row["Category"].lower()
                        if any(word in category for word in needs_keywords):
                            return "Needs"
                        elif any(word in category for word in wants_keywords):
                            return "Wants"
                        elif any(word in category for word in savings_keywords):
                            return "Savings"
                        else:
                            return "Needs"  # default fallback

                    df["Group"] = df.apply(classify, axis=1)
                    actual_summary = df.groupby("Group")["Amount"].sum().reset_index()
                    actual_summary.columns = ["Type", "Actual Spending"]

                    summary = pd.merge(budget_data, actual_summary, on="Type", how="left").fillna(0)
                    st.dataframe(summary)

                    # Bar chart comparison
                    st.subheader("📉 Budget vs. Actual Comparison")
                    fig2, ax2 = plt.subplots()
                    bar_width = 0.35
                    x = range(len(summary))

                    ax2.bar(x, summary["Budgeted Amount"], width=bar_width, label="Budgeted")
                    ax2.bar([p + bar_width for p in x], summary["Actual Spending"], width=bar_width, label="Actual")
                    ax2.set_xticks([p + bar_width / 2 for p in x])
                    ax2.set_xticklabels(summary["Type"])
                    ax2.set_ylabel("Amount ($)")
                    ax2.set_title("Budgeted vs. Actual Spending")
                    ax2.legend()
                    st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error generating budget summary: {e}")

# Add download buttons if there is summary data
if not summary_df.empty:
    st.markdown("### 📥 Export Budget Summary")

    # CSV export
    csv_buffer = io.StringIO()
    summary_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download as CSV",
        data=csv_buffer.getvalue(),
        file_name="budget_summary.csv",
        mime="text/csv"
    )

    # Excel export
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
        writer.save()
    st.download_button(
        label="Download as Excel",
        data=excel_buffer.getvalue(),
        file_name="budget_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
