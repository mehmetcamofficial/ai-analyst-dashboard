import streamlit as st
from db import create_user, check_login

def login_system():

    st.sidebar.markdown("## 🧠 AI SaaS Login")

    st.sidebar.markdown("---")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    mode = st.sidebar.radio("Mode", ["Login", "Register"])

    login_btn = st.sidebar.button("🚀 Continue")

    user = None

    if login_btn:

        if username and password:

            if mode == "Register":
                create_user(username, password)
                st.sidebar.success("✅ Account created")

            elif mode == "Login":

                if check_login(username, password):
                    st.session_state["user"] = username
                    user = username
                    st.sidebar.success("🎉 Login successful")
                else:
                    st.sidebar.error("❌ Invalid credentials")

    if "user" in st.session_state:
        user = st.session_state["user"]

    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 **AI Analyst Pro SaaS**")
    st.sidebar.caption("Modern AI dashboard system")

    return user
