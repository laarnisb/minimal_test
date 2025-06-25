import streamlit as st

if st.button("Test Connection"):
    try:
        server_time = test_connection()
        if server_time:
            st.success(f"🎉 Connected! Server time: {server_time}")
        else:
            st.warning("Connected, but server time is not available.")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
