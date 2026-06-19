"""Session state + persistence for Clearwork.

Same pattern as Team OS: JSON file now, backend swappable later.
Contributions and confirmations are append-only in the data model;
the store just serializes and deserializes.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from clearwork.models import (
    Confirmation, Contribution, Member, Project,
    confirmation_from_dict, contribution_from_dict,
    member_from_dict, project_from_dict,
)

_FILE = Path("clearwork_state.json")


def _load() -> dict | None:
    if not _FILE.exists():
        return None
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _serialize(st) -> dict:
    ss = st.session_state
    return {
        "members": [m.__dict__.copy() for m in ss.members],
        "projects": [p.__dict__.copy() for p in ss.projects],
        "contributions": [c.__dict__.copy() for c in ss.contributions],
        "confirmations": [c.__dict__.copy() for c in ss.confirmations],
    }


def save(st) -> None:
    _FILE.write_text(json.dumps(_serialize(st), indent=2), encoding="utf-8")


def init_state(st) -> None:
    ss = st.session_state
    if ss.get("_inited"):
        return
    saved = _load() or {}
    ss.members = [member_from_dict(d) for d in saved.get("members", [])]
    ss.projects = [project_from_dict(d) for d in saved.get("projects", [])]
    ss.contributions = [contribution_from_dict(d) for d in saved.get("contributions", [])]
    ss.confirmations = [confirmation_from_dict(d) for d in saved.get("confirmations", [])]
    ss._inited = True


def load_demo(st) -> None:
    """A sample project with mixed confirmation states."""
    ss = st.session_state
    members = [Member.create("Avery", "Lead"), Member.create("Ben", "Builder"),
               Member.create("Chen", "Designer"), Member.create("Dee", "Outreach")]
    ss.members = members
    a, b, c, d = members

    proj = Project.create("HackMAC 2026", "48-hour hackathon — built an accessibility tool")
    ss.projects = [proj]

    contribs = [
        Contribution.create(a.id, a.name, proj.id, "Built the backend API",
                            "Flask REST API with SQLite", "Build"),
        Contribution.create(a.id, a.name, proj.id, "Set up CI/CD pipeline",
                            "GitHub Actions for auto-deploy", "Build"),
        Contribution.create(b.id, b.name, proj.id, "Built the frontend",
                            "React dashboard with accessibility features", "Build"),
        Contribution.create(c.id, c.name, proj.id, "Designed the UI",
                            "Figma mockups and branding", "Design"),
        Contribution.create(c.id, c.name, proj.id, "Created the pitch deck",
                            "12-slide story arc", "Pitch"),
        Contribution.create(d.id, d.name, proj.id, "Handled event logistics",
                            "Team registration and travel", "Organize"),
        # Dee also claims a contribution that peers will dispute
        Contribution.create(d.id, d.name, proj.id, "Co-wrote the pitch script",
                            "", "Pitch"),
    ]
    ss.contributions = contribs

    # Confirmations: most confirmed, one adjusted, one disputed
    confirms = []
    # Avery's API — confirmed by all
    for reviewer in [b, c, d]:
        cf = Confirmation.create(contribs[0].id, reviewer.id, reviewer.name)
        cf.status = "confirmed"
        cf.reviewed_on = date.today().isoformat()
        confirms.append(cf)
    # Ben's frontend — confirmed
    for reviewer in [a, c]:
        cf = Confirmation.create(contribs[2].id, reviewer.id, reviewer.name)
        cf.status = "confirmed"
        cf.reviewed_on = date.today().isoformat()
        confirms.append(cf)
    # Chen's UI — confirmed
    cf = Confirmation.create(contribs[3].id, a.id, a.name)
    cf.status = "confirmed"
    cf.reviewed_on = date.today().isoformat()
    confirms.append(cf)
    # Chen's pitch deck — adjusted
    cf = Confirmation.create(contribs[4].id, a.id, a.name)
    cf.status = "adjusted"
    cf.note = "Chen designed the slides but Avery wrote most of the script"
    cf.reviewed_on = date.today().isoformat()
    confirms.append(cf)
    # Dee's logistics — confirmed
    cf = Confirmation.create(contribs[5].id, a.id, a.name)
    cf.status = "confirmed"
    cf.reviewed_on = date.today().isoformat()
    confirms.append(cf)
    # Dee's "co-wrote pitch" — disputed
    cf = Confirmation.create(contribs[6].id, c.id, c.name)
    cf.status = "disputed"
    cf.note = "Dee wasn't in the pitch prep sessions"
    cf.reviewed_on = date.today().isoformat()
    confirms.append(cf)
    # Avery's CI/CD — pending (not yet reviewed)
    cf = Confirmation.create(contribs[1].id, b.id, b.name)
    confirms.append(cf)

    ss.confirmations = confirms
    save(st)
