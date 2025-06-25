from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st
import os

# Read secrets from Streamlit config
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT now()"))
            st.success(f"🎉 Connected! Server time: {result.scalar()}")
    except SQLAlchemyError as e:
        st.error(f"Connection failed: {e}")

def insert_transaction(user_id, name, amount, category):
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO transactions (user_id, name, amount, category, created_at)
                    VALUES (:user_id, :name, :amount, :category, NOW())
                """),
                {"user_id": user_id, "name": name, "amount": amount, "category": category}
            )
            st.success("✅ Transaction added successfully!")
    except SQLAlchemyError as e:
        st.error(f"Error inserting transaction: {e}")

def get_transactions_by_user(user_id):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM transactions WHERE user_id = :user_id ORDER BY created_at DESC"),
                {"user_id": user_id}
            )
            return result.fetchall()
    except SQLAlchemyError as e:
        st.error(f"Error retrieving transactions: {e}")
        return []
