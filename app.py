import streamlit as st
from database import test_connection, insert_transaction, get_transactions_by_user

st.title("💸 WiseBudget Tracker")

test_connection()

st.subheader("Add Transaction")
user_id = st.text_input("User ID (uuid)")
name = st.text_input("Transaction Name")
amount = st.number_input("Amount", min_value=0.0, step=0.01)
category = st.selectbox("Category", ["Needs", "Wants", "Savings"])

if st.button("Submit Transaction"):
    if user_id and name and amount and category:
        insert_transaction(user_id, name, amount, category)
    else:
        st.warning("Please fill out all fields.")

st.subheader("View Transactions")
if user_id:
    transactions = get_transactions_by_user(user_id)
    if transactions:
        for row in transactions:
            st.write(dict(row))
    else:
        st.info("No transactions found.")
