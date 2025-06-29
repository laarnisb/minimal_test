from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import streamlit as st
import pandas as pd

# Initialize SQLAlchemy engine using Streamlit secrets
engine = create_engine(st.secrets["DATABASE_URL"])

def get_engine():
    """Return a new database engine instance."""
    return create_engine(st.secrets["DATABASE_URL"])

def test_connection():
    """Test the connection to the database by returning the current timestamp."""
    with engine.connect() as conn:
        return conn.execute(text("SELECT NOW()")).scalar()

def insert_user(name, email, registration_date):
    """Insert a new user into the users table."""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users (name, email, registration_date) VALUES (:name, :email, :date)"),
                {"name": name, "email": email, "date": registration_date}
            )
    except IntegrityError as e:
        if 'users_email_key' in str(e.orig):
            raise ValueError(f"⚠️ User with email '{email}' is already registered.")
        else:
            raise ValueError(f"❌ Failed to register user: {str(e)}")

def insert_transactions(df: pd.DataFrame):
    """Insert multiple transactions into the transactions table."""
    with engine.connect() as conn:
        for _, row in df.iterrows():
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": row["user_email"]}
            )
            user_row = result.fetchone()

            if not user_row:
                raise ValueError(f"❌ User with email '{row['user_email']}' not found in users table.")

            user_id = user_row[0]

            conn.execute(
                text("""
                    INSERT INTO transactions (user_id, amount, category, description, date)
                    VALUES (:user_id, :amount, :category, :description, :date)
                """),
                {
                    "user_id": user_id,
                    "amount": row["amount"],
                    "category": row["category"],
                    "description": row["description"],
                    "date": row["date"]
                }
            )

def get_all_transactions():
    """Fetch all transaction records from the transactions table."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM transactions"))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

def add_user_email_column():
    """Add 'user_email' column to transactions table if it does not exist."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'transactions' AND column_name = 'user_email'
        """))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE transactions ADD COLUMN user_email TEXT"))
