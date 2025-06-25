import streamlit as st
from sqlalchemy import create_engine, text

# Set page configuration
st.set_page_config(page_title="Minimal Test App", layout="centered")
st.title("🔌 Database Connection Test")

# Construct connection string using secrets
db_url = f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@" \
         f"{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"

# Create the engine
engine = create_engine(db_url)

# Attempt to connect and fetch the server time
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()")).fetchone()
        st.success(f"🎉 Connected! Server time: {result[0]}")
except Exception as e:
    st.error(f"❌ Connection failed: {e}")
