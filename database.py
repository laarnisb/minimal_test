from sqlalchemy import create_engine, text
import streamlit as st
import pandas as pd

# Initialize SQLAlchemy engine using Streamlit secrets
engine = create_engine(st.secrets["DATABASE_URL"])

# Return the engine so it can be reused in other scripts
def get_engine():
    db_url = st.secrets["DATABASE_URL"]
    return create_engine(db_url)

# Test connection to ensure the app is connected to the database
def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()")).scalar()
    return result

# Insert a new user into the users table
def insert_user(name, email, registration_date):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (name, email, registration_date) VALUES (:name, :email, :date)"),
            {"name": name, "email": email, "date": registration_date}
        )

# Insert transaction records from a dataframe into the transactions table
def insert_transactions(df: pd.DataFrame):
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("INSERT INTO transactions (user_email, amount, category, description, created_at) "
                     "VALUES (:user_email, :amount, :category, :description, :created_at)"),
                {
                    "user_email": row["user_email"],
                    "amount": row["amount"],
                    "category": row["category"],
                    "description": row["description"],
                    "created_at": row["created_at"]
                }
            )

# Retrieve all transactions for viewing
def get_all_transactions():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM transactions"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df
