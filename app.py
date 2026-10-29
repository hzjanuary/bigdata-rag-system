"""Optional Streamlit client. Talks only to authenticated API; no direct storage access."""
import os

import httpx
import streamlit as st

st.set_page_config(page_title="Workspace RAG")
st.title("Workspace RAG")
api = os.environ.get("RAG_API_URL", "http://127.0.0.1:8000")
token = st.text_input("Workspace capability", type="password")
if not token:
    st.stop()
headers = {"Authorization": "Bearer " + token}
try:
    with httpx.Client(base_url=api, headers=headers, timeout=30, trust_env=False) as client:
        response = client.get("/workspaces")
        if response.status_code != 200:
            st.error("Authentication failed")
            st.stop()
        workspaces = response.json()
        if not workspaces:
            st.info("No authorized workspace")
            st.stop()
        selected = st.selectbox("Workspace", workspaces, format_func=lambda w: w["slug"])
        question = st.text_input("Search your documents")
        if st.button("Search") and question:
            result = client.post(f'/workspaces/{selected["id"]}/search', json={"query": question})
            if result.status_code != 200:
                st.error("Search unavailable")
            else:
                for match in result.json()["matches"]:
                    st.text(match["excerpt"])
                    st.caption(f'{match["filename"]} / page {match["page"]} / {match["citation"]}')
except httpx.HTTPError:
    st.error("API unavailable")
