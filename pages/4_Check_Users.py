from sqlalchemy import text
from database import get_engine
import pandas as pd
import streamlit as st

st.title("Check Users")

engine = get_engine()

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        st.dataframe(df)
except Exception as e:
    st.error(f"❌ Error querying users table: {e}")
