"""Log — each person records what they delivered.

Deliberately tracks deliverables, not hours. "Built the login page" invites
accountability; "worked 8 hours" invites gaming. Category and workstream/rock
are optional connections back to Team OS structure.
"""

import streamlit as st

from clearwork.gate import require_access
from clearwork.models import Contribution
from clearwork.store import init_state, save

st.set_page_config(page_title="Log · Clearwork", page_icon="📝", layout="wide")
init_state(st)
require_access()

st.title("📝 Log Contributions")
st.caption("Record what you *delivered*, not how long you spent. Deliverables "
           "are what peers can verify and what a resume card can show.")

members = st.session_state.members
projects = st.session_state.projects

if not members or not projects:
    st.warning("Add members and a project on the **Team Setup** page first.")
    st.stop()

CATEGORIES = ["Build", "Design", "Pitch", "Research", "Organize", "Other"]

# ── Log a contribution ────────────────────────────────────────────────────────
with st.form("log_contribution", clear_on_submit=True):
    who = st.selectbox("Who did it?", members, format_func=lambda m: m.name)
    proj = st.selectbox("Project", projects, format_func=lambda p: p.name)
    title = st.text_input("What was delivered?",
                          placeholder="e.g. Built the login page")
    desc = st.text_area("Details (optional)",
                        placeholder="What specifically, any links or evidence")
    cols = st.columns(3)
    cat = cols[0].selectbox("Category", [""] + CATEGORIES)
    workstream = cols[1].text_input("Workstream (from Team OS, optional)")
    rock = cols[2].text_input("Rock (from Team OS, optional)")

    if st.form_submit_button("Log contribution", type="primary"):
        if not title.strip():
            st.error("What was delivered is required.")
        else:
            st.session_state.contributions.append(Contribution.create(
                who.id, who.name, proj.id, title, desc, cat, workstream, rock,
            ))
            save(st)
            st.success(f"Logged for {who.name}.")
            st.rerun()

st.divider()

# ── Existing contributions ────────────────────────────────────────────────────
st.markdown("#### Logged contributions")
proj_filter = st.selectbox("Filter by project",
                           [None] + projects,
                           format_func=lambda p: "All projects" if p is None else p.name)

contribs = st.session_state.contributions
if proj_filter:
    contribs = [c for c in contribs if c.project_id == proj_filter.id]

if not contribs:
    st.caption("No contributions logged yet.")
else:
    for c in reversed(contribs):
        cat_tag = f" `{c.category}`" if c.category else ""
        st.markdown(f"**{c.title}**{cat_tag} — {c.member_name} · {c.logged_on}")
        if c.description:
            st.caption(c.description)
