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
                text("INSERT INTO transactions (user_email, amount, category, description, date) "
                     "VALUES (:user_email, :amount, :category, :description, :date)"),
                {
                    "user_email": row["user_email"],
                    "amount": row["amount"],
                    "category": row["category"],
                    "description": row["description"],
                    "date": row["date"]
                }
            )

# Retrieve all transactions for viewing
def get_all_transactions():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM transactions"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

# Add a 'user_email' column to transactions table if it doesn't exist
def add_user_email_column_if_missing():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'transactions' AND column_name = 'user_email'
        """))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE transactions ADD COLUMN user_email TEXT"))

# Check and add user_email column to transactions table if not exists
def add_user_email_column():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='transactions' AND column_name='user_email'
        """))
        column_exists = result.fetchone() is not None

        if not column_exists:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN user_email TEXT"))
