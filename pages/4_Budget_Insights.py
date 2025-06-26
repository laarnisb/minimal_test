import streamlit as st
from database import get_engine
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Budget Insights", page_icon="📊")
st.title("📊 Budget Insights")

engine = get_engine()

def fetch_transactions():
    query = "SELECT amount, category FROM transactions"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

try:
    df = fetch_transactions()

    if df.empty:
        st.info("No transactions found.")
    else:
        summary = df.groupby("category")["amount"].sum().reset_index()

        st.subheader("Spending Summary")
        st.dataframe(summary)

        fig = px.pie(summary, names="category", values="amount", title="Spending by Category")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading insights: {e}")
