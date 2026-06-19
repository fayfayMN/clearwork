"""Resume Card — the payoff.

Generate a verified, portable summary of what someone did on a project. People
tolerate being measured when they get something valuable back — and a
peer-confirmed project card beats a self-reported resume bullet.
"""

import streamlit as st

from clearwork import resume_card
from clearwork.store import init_state

st.set_page_config(page_title="Resume Card · Clearwork", page_icon="🏆", layout="wide")
init_state(st)

st.title("🏆 Resume Card")
st.caption("Generate a verified project card for any team member. Peer "
           "confirmations make it credible — each contribution shows its "
           "verification status.")

members = st.session_state.members
projects = st.session_state.projects
contributions = st.session_state.contributions
confirmations = st.session_state.confirmations

if not members or not projects:
    st.warning("Add members and a project on the **Team Setup** page first.")
    st.stop()

# ── Select member + project ───────────────────────────────────────────────────
cols = st.columns(2)
member = cols[0].selectbox("Member", members, format_func=lambda m: m.name)
project = cols[1].selectbox("Project", projects, format_func=lambda p: p.name)

# Filter contributions and confirmations for this member + project
my_contribs = [c for c in contributions
               if c.member_id == member.id and c.project_id == project.id]
contrib_ids = {c.id for c in my_contribs}
my_confirms = [cf for cf in confirmations if cf.contribution_id in contrib_ids]

if not my_contribs:
    st.info(f"No contributions logged for {member.name} on {project.name}.")
    st.stop()

# ── Generate card ─────────────────────────────────────────────────────────────
card = resume_card.generate(
    member.name, member.role, project.name, project.description,
    my_contribs, my_confirms, members,
)

st.divider()
st.markdown(card)

st.divider()
st.download_button("Download resume-card.md", card,
                   file_name=f"resume_card_{member.name.lower().replace(' ', '_')}.md")
st.caption("Paste into LinkedIn, your portfolio, or a job application. "
           "The verification status speaks for itself.")
