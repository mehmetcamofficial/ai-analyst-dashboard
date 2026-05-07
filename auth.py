import streamlit as st

def login():
    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username")

    if username:
        st.session_state["user"] = username
        return username

    return None
