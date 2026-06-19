"""Team Setup — members and projects."""

import streamlit as st

from clearwork.models import Member, Project
from clearwork.store import init_state, save

st.set_page_config(page_title="Team Setup · Clearwork", page_icon="👥", layout="wide")
init_state(st)

st.title("👥 Team Setup")
st.caption("Add your team members and create projects. A project is any bounded "
           "piece of work — a hackathon, a quarter, a product launch.")

# ── Members ───────────────────────────────────────────────────────────────────
st.markdown("#### Members")
with st.form("add_member", clear_on_submit=True):
    cols = st.columns([2, 2, 1])
    m_name = cols[0].text_input("Name")
    m_role = cols[1].text_input("Role (optional)", placeholder="e.g. Engineer, Designer")
    if cols[2].form_submit_button("Add") and m_name.strip():
        st.session_state.members.append(Member.create(m_name, m_role))
        save(st)
        st.rerun()

for m in st.session_state.members:
    c1, c2 = st.columns([5, 1])
    c1.write(f"**{m.name}**" + (f" — {m.role}" if m.role else ""))
    if c2.button("Remove", key=f"rm_{m.id}"):
        st.session_state.members = [x for x in st.session_state.members
                                    if x.id != m.id]
        save(st)
        st.rerun()

if not st.session_state.members:
    st.caption("No members yet.")

st.divider()

# ── Projects ──────────────────────────────────────────────────────────────────
st.markdown("#### Projects")
with st.form("add_project", clear_on_submit=True):
    cols = st.columns([2, 3, 1])
    p_name = cols[0].text_input("Project name")
    p_desc = cols[1].text_input("Description (optional)")
    if cols[2].form_submit_button("Create") and p_name.strip():
        st.session_state.projects.append(Project.create(p_name, p_desc))
        save(st)
        st.rerun()

STATUS_LABEL = {"active": "Active", "completed": "Completed", "archived": "Archived"}
for p in st.session_state.projects:
    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.markdown(f"**{p.name}**" + (f" — {p.description}" if p.description else ""))
        c1.caption(f"Started {p.started_on}")
        new_status = c2.selectbox("Status", list(STATUS_LABEL.keys()),
                                  index=list(STATUS_LABEL.keys()).index(p.status),
                                  format_func=lambda s: STATUS_LABEL[s],
                                  key=f"ps_{p.id}", label_visibility="collapsed")
        if new_status != p.status:
            p.status = new_status
            if new_status == "completed" and not p.completed_on:
                from datetime import date
                p.completed_on = date.today().isoformat()
            save(st)
        if c3.button("Delete", key=f"dp_{p.id}"):
            st.session_state.projects = [x for x in st.session_state.projects
                                         if x.id != p.id]
            save(st)
            st.rerun()

if not st.session_state.projects:
    st.caption("No projects yet.")
