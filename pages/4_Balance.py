"""Balance — is work distributed fairly?

Not a leaderboard. The point is to catch imbalances early: heroes carrying
too much, ghosts contributing nothing, disputed claims unresolved. The
analysis is deterministic and explainable — same philosophy as Team OS.
"""

import streamlit as st

from clearwork.gate import require_access
from clearwork import balance
from clearwork.store import init_state

st.set_page_config(page_title="Balance · Clearwork", page_icon="⚖️", layout="wide")
init_state(st)
require_access()

st.title("⚖️ Contribution Balance")
st.caption("Is work distributed fairly? This isn't a ranking — it's an early "
           "warning system for heroes, ghosts, and disputed claims.")

members = st.session_state.members
projects = st.session_state.projects
contributions = st.session_state.contributions
confirmations = st.session_state.confirmations

if not members:
    st.warning("Add members on the **Team Setup** page first.")
    st.stop()

# ── Project filter ────────────────────────────────────────────────────────────
proj_filter = st.selectbox("Project",
                           [None] + projects,
                           format_func=lambda p: "All projects" if p is None else p.name)
project_id = proj_filter.id if proj_filter else None

result = balance.analyze(members, contributions, confirmations, project_id)

# ── Distribution bars ─────────────────────────────────────────────────────────
st.markdown("#### Distribution")
if result["per_member"]:
    for pm in sorted(result["per_member"], key=lambda x: -x["count"]):
        pct = pm["pct"]
        confirm_text = ""
        if pm["confirm_rate"] is not None:
            confirm_text = f" · {pm['confirm_rate']}% confirmed"
        cats = f" · {', '.join(pm['categories'])}" if pm["categories"] else ""

        st.write(f"**{pm['name']}** — {pm['count']} contribution(s) ({pct}%)"
                 f"{confirm_text}{cats}")
        st.progress(min(pct / 100, 1.0))

st.divider()

# ── Findings ──────────────────────────────────────────────────────────────────
st.markdown("#### Health check")
st.caption(result["summary"])
for f in result["findings"]:
    if f["level"] == "error":
        st.error(f["msg"])
    elif f["level"] == "warn":
        st.warning(f["msg"])
    else:
        st.success(f["msg"])
