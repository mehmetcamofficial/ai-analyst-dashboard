import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="AI Analyst Dashboard", layout="wide")

# API KEY (Streamlit Cloud + local uyumlu)
API_KEY = st.secrets.get("POLLINATIONS_API_KEY", "")

st.title("🧠 Personal AI Analyst Dashboard")
st.caption("AI-powered analysis system (Pollinations + Streamlit)")

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("⚙️ Settings")

task = st.sidebar.selectbox(
    "Task Type",
    ["Data Insight", "Market Analysis", "Summary", "Custom Prompt"]
)

model = st.sidebar.selectbox(
    "Model",
    ["gpt-4o-mini", "fast-model"]
)

# -------------------------
# INPUT
# -------------------------
user_input = st.text_area("📥 Enter your data / question")

# -------------------------
# AI CALL
# -------------------------
def call_ai(prompt):
    if not API_KEY:
        return "❌ API key missing. Add POLLINATIONS_API_KEY in secrets."

    url = "https://api.pollinations.ai/text"

    response = requests.post(url, json={
        "prompt": prompt,
        "model": model,
        "api_key": API_KEY
    })

    try:
        return response.json()
    except:
        return response.text

# -------------------------
# MAIN LOGIC
# -------------------------
if st.button("🚀 Analyze") and user_input:

    if task == "Data Insight":
        prompt = f"Analyze this data and give insights:\n{user_input}"

    elif task == "Market Analysis":
        prompt = f"Perform market analysis:\n{user_input}"

    elif task == "Summary":
        prompt = f"Summarize this:\n{user_input}"

    else:
        prompt = user_input

    with st.spinner("AI is thinking..."):
        result = call_ai(prompt)

    st.subheader("📊 Result")
    st.write(result)

# -------------------------
# CSV MODULE (MVP)
# -------------------------
st.divider()
st.subheader("📁 CSV Analysis (Basic)")

file = st.file_uploader("Upload CSV")

if file:
    df = pd.read_csv(file)
    st.write(df.head())

    if st.button("Analyze CSV"):
        prompt = f"Analyze this dataset:\n{df.to_string()}"

        with st.spinner("Analyzing dataset..."):
            result = call_ai(prompt)

        st.write(result)
