import streamlit as st
from db import check_login, create_user

def login():

    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    mode = st.sidebar.radio("Mode", ["Login", "Register"])

    if username and password:

        if mode == "Register":
            create_user(username, password)
            st.sidebar.success("Account created")

        if mode == "Login":
            if check_login(username, password):
                st.session_state["user"] = username
                return username
            else:
                st.sidebar.error("Invalid credentials")

    return None
