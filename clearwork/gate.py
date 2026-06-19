"""Access gate — password-protect every page."""

import streamlit as st


def require_access():
    """Show a login wall if the user hasn't entered the access code yet.

    Set the code in Streamlit Cloud → App settings → Secrets:
        access_code = "your-secret-here"
    """
    if st.session_state.get("authenticated"):
        return

    st.markdown("## 🔒 Access required")
    st.markdown("This app is **invite-only**. Enter the access code provided "
                "by the team owner to continue.")

    code = st.text_input("Access code", type="password",
                         placeholder="Paste the code you received")

    if st.button("Enter", type="primary"):
        expected = st.secrets.get("access_code", "")
        if expected and code == expected:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect access code. Contact the team owner for access.")

    st.divider()
    st.caption("© 2026 Feifei Li. All rights reserved. "
               "Clearwork is proprietary software.")
    st.stop()
