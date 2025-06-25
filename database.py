import streamlit as st
from sqlalchemy import create_engine

# Load database credentials from Streamlit secrets
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10}, pool_pre_ping=True)
