import streamlit as st
from database import get_engine
import pandas as pd

st.set_page_config(page_title="Check Users", page_icon="🧾")
st.title("🧾 Debug: Check Registered Users")

try:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM users")
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=result.keys())
        st.dataframe(df)

        if df.empty:
            st.warning("⚠️ No users found in the users table.")
        else:
            st.success("✅ Fetched users table successfully.")
except Exception as e:
    st.error(f"❌ Error querying users table: {e}")
