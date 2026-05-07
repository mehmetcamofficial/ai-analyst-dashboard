import streamlit as st
from db import create_user, check_login

def login_system():

    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    mode = st.sidebar.radio("Mode", ["Login", "Register"])

    user = None

    if username and password:

        if mode == "Register":
            create_user(username, password)
            st.sidebar.success("Account created")

        if mode == "Login":
            if check_login(username, password):
                st.session_state["user"] = username
                user = username
                st.sidebar.success("Login success")
            else:
                st.sidebar.error("Invalid credentials")

    if "user" in st.session_state:
        user = st.session_state["user"]

    return user
