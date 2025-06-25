from sqlalchemy import create_engine
import streamlit as st

def test_connection():
    try:
        db_user = st.secrets["DB_USER"]
        db_password = st.secrets["DB_PASSWORD"]
        db_host = st.secrets["DB_HOST"]
        db_port = st.secrets["DB_PORT"]
        db_name = st.secrets["DB_NAME"]

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            if result.scalar() == 1:
                st.success("✅ Database connection successful.")
            else:
                st.warning("⚠️ Connection attempted but returned unexpected result.")

    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
