"""Clearwork — Streamlit app entry (Home).

Track who did what, confirm it with peers, and turn the record into portable
proof. The PROVE stage that complements TeamUp (FORM) and Team OS (RUN).

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st

from clearwork.store import init_state, load_demo, save

st.set_page_config(page_title="Clearwork", page_icon="🔍", layout="wide")
init_state(st)

st.title("🔍 Clearwork")
st.caption("Track who did what, confirm it with peers, and turn the record into "
           "verified proof. Contributions are deliverables, not hours — and "
           "verification is by teammates, not managers.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Members", len(st.session_state.members))
c2.metric("Projects", len(st.session_state.projects))
c3.metric("Contributions", len(st.session_state.contributions))
pending = sum(1 for cf in st.session_state.confirmations if cf.status == "pending")
c4.metric("Pending reviews", pending)

st.info("Everything is deterministic and explainable — no API key, no cost. "
        "Data persists to `clearwork_state.json`.", icon="🔒")

st.divider()
st.markdown(
    "#### How it works\n"
    "1. **Team Setup** — add members and create a project\n"
    "2. **Log** — each person logs what they *delivered* (not hours)\n"
    "3. **Confirm** — peers verify each other's contributions (yes / adjust / dispute)\n"
    "4. **Balance** — see if work is distributed fairly; surface heroes and ghosts\n"
    "5. **Resume Card** — generate a verified, portable proof of contribution\n"
)

st.markdown("#### Where this fits")
st.markdown(
    "- **TeamUp** — *form* a healthy team (matching + kickoff)\n"
    "- **Team OS** — *run* it healthily (charter, RACI, decisions, health pulse)\n"
    "- **Clearwork (this app)** — *prove* who contributed; reputation flows back\n"
)

st.divider()
bc1, bc2, _ = st.columns([1, 1, 2])
if bc1.button("Load demo project",
              help="A sample hackathon with mixed confirmations"):
    load_demo(st)
    st.rerun()
if bc2.button("Reset everything", help="Clear all data"):
    for k in ("members", "projects", "contributions", "confirmations", "_inited"):
        st.session_state.pop(k, None)
    init_state(st)
    save(st)
    st.rerun()

st.divider()
st.caption("© 2026 Feifei Li. All rights reserved. "
           "Clearwork is proprietary software — source available for review only. "
           "Commercial use requires written permission.")
