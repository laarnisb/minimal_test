import streamlit as st
import pandas as pd
import plotly.express as px
import io
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Budget Summary Reports", page_icon="📑")
st.title("📑 Budget Summary Reports")

st.write("Enter your registered email to generate your budget summary report.")

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

                # Step 2: Get transactions
                txn_query = text("SELECT category, amount FROM transactions WHERE user_id = :user_id")
                txn_df = pd.read_sql(txn_query, conn, params={"user_id": user_id})

                if not txn_df.empty:
                    # Step 3: Map to budget groups
                    category_mapping = {
                        "groceries": "Needs", "rent": "Needs", "utilities": "Needs", "transport": "Needs",
                        "insurance": "Needs", "healthcare": "Needs", "internet": "Needs",
                        "dining": "Wants", "entertainment": "Wants", "travel": "Wants", "shopping": "Wants",
                        "subscriptions": "Wants",  "savings": "Savings", "investment": "Savings",
                        "emergency fund": "Savings", "retirement": "Savings"
                    }
                    txn_df["Group"] = txn_df["category"].map(category_mapping).fillna("Other")

                    # Step 4: Summarize
                    summary_df = txn_df.groupby("Group")["amount"].sum().reset_index()
                    summary_df.columns = ["Category Group", "Total Spending"]

                    # Step 5: Display
                    st.subheader("💡 Spending Breakdown")
                    st.dataframe(summary_df)

                    fig = px.pie(summary_df, names="Category Group", values="Total Spending",
                                 title="Spending Distribution by Category Group")
                    st.plotly_chart(fig, use_container_width=True)

                    # Step 6: Export to Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        summary_df.to_excel(writer, sheet_name="Summary", index=False)
                    output.seek(0)

                    st.download_button(
                        label="📥 Download Report as Excel",
                        data=output,
                        file_name="budget_summary_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                else:
                    st.info("ℹ️ No transactions found for this user.")
            else:
                st.warning("⚠️ No user found with that email.")
    except Exception as e:
        st.error(f"❌ Error generating report: {e}")
