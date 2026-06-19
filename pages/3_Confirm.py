"""Confirm — peers verify each other's contributions.

Not a rating. Not a performance review. A factual check: did this person
do what they say they did? Yes / Partly (with a note) / No (with a note).

You can't confirm your own contribution — that's the whole point.
"""

from datetime import date

import streamlit as st

from clearwork.models import CONFIRM_CODES, Confirmation
from clearwork.store import init_state, save

st.set_page_config(page_title="Confirm · Clearwork", page_icon="✅", layout="wide")
init_state(st)

st.title("✅ Peer Confirmation")
st.caption("Review your teammates' contributions. This isn't a rating — it's a "
           "factual check: did they do what they logged? Your confirmations make "
           "their resume card credible.")

members = st.session_state.members
contributions = st.session_state.contributions
confirmations = st.session_state.confirmations

if not members:
    st.warning("Add members on the **Team Setup** page first.")
    st.stop()

# ── Select reviewer ───────────────────────────────────────────────────────────
reviewer = st.selectbox("I am:", members, format_func=lambda m: m.name)

# ── Contributions to review (not your own) ────────────────────────────────────
others = [c for c in contributions if c.member_id != reviewer.id]
if not others:
    st.info("No contributions from other members to review yet.")
    st.stop()

# Build lookup: which contributions has this reviewer already reviewed?
my_confirms = {cf.contribution_id: cf for cf in confirmations
               if cf.reviewer_id == reviewer.id}

pending_contribs = [c for c in others if c.id not in my_confirms]
reviewed_contribs = [c for c in others if c.id in my_confirms]

st.markdown(f"#### Pending review ({len(pending_contribs)})")

if not pending_contribs:
    st.success("You've reviewed everything. Thank you.")
else:
    for c in pending_contribs:
        with st.container(border=True):
            st.markdown(f"**{c.title}**")
            cat_tag = f" `{c.category}`" if c.category else ""
            st.caption(f"By {c.member_name} · {c.logged_on}{cat_tag}")
            if c.description:
                st.write(c.description)

            cols = st.columns([2, 3, 1])
            status = cols[0].selectbox(
                "Your verdict", ["confirmed", "adjusted", "disputed"],
                format_func=lambda s: CONFIRM_CODES.get(s, s),
                key=f"v_{c.id}",
            )
            note = cols[1].text_input(
                "Note (required for adjusted/disputed)",
                key=f"n_{c.id}",
                placeholder="What specifically needs adjusting?",
            )
            if cols[2].button("Submit", key=f"s_{c.id}"):
                if status in ("adjusted", "disputed") and not note.strip():
                    st.error("Please explain what needs adjusting or why you dispute.")
                else:
                    cf = Confirmation.create(c.id, reviewer.id, reviewer.name)
                    cf.status = status
                    cf.note = note.strip()
                    cf.reviewed_on = date.today().isoformat()
                    st.session_state.confirmations.append(cf)
                    save(st)
                    st.rerun()

# ── Already reviewed ──────────────────────────────────────────────────────────
if reviewed_contribs:
    with st.expander(f"Already reviewed ({len(reviewed_contribs)})"):
        for c in reviewed_contribs:
            cf = my_confirms[c.id]
            icon = {"confirmed": "✅", "adjusted": "🟡", "disputed": "🔴"}
            st.markdown(f"{icon.get(cf.status, '❓')} **{c.title}** "
                        f"(by {c.member_name}) — {cf.status}")
            if cf.note:
                st.caption(f"Your note: {cf.note}")
