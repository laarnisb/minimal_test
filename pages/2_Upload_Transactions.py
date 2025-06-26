import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine

st.set_page_config(page_title="Upload Transactions", page_icon="📤")
st.title("📤 Upload Transactions")

# 1. File uploader
uploaded_file = st.file_uploader("Upload your transaction CSV file", type="csv")

# 2. Get database engine
engine = get_engine()

# 3. Fetch users for linking uploaded data
with engine.connect() as conn:
    users = conn.execute(text("SELECT id, name FROM users")).fetchall()
user_dict = {user.name: str(user.id) for user in users}

# 4. Let user choose which user to assign uploaded transactions to
selected_user = st.selectbox("Assign transactions to user", options=list(user_dict.keys()))
user_id = user_dict[selected_user] if selected_user else None

# 5. Required columns
REQUIRED_COLUMNS = ["date", "amount", "category", "description"]

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Preview")
        st.dataframe(df)

        # 6. Validate columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
        else:
            if st.button("Upload Transactions"):
                df["user_id"] = user_id  # Add user ID column

                with engine.begin() as conn:  # begin() handles transaction commit
                    for _, row in df.iterrows():
                        stmt = text("""
                            INSERT INTO transactions (user_id, date, amount, category, description, created_at)
                            VALUES (:user_id, :date, :amount, :category, :description, NOW())
                        """)
                        conn.execute(stmt, {
                            "user_id": row["user_id"],
                            "date": row["date"],
                            "amount": row["amount"],
                            "category": row["category"],
                            "description": row["description"]
                        })

                st.success(f"✅ Successfully uploaded {len(df)} transactions!")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
