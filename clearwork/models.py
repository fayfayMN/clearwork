"""Entities for Clearwork.

Contribution tracking is politically sensitive — the data model is designed
to make gaming hard and fairness visible:

- Contributions are *deliverables*, not hours. "Built the login page" not
  "worked 8 hours." Hours invite gaming; deliverables invite accountability.
- Peer confirmation is yes/no/adjust, not a rating. Ratings create politics;
  confirmations create a factual record.
- Everything is append-only where it matters (contributions, confirmations).
  You can't rewrite history after the fact.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

SCHEMA_VERSION = 1

CONFIRM_CODES = {
    "confirmed": "Yes — this happened as described",
    "adjusted": "Partly — needs adjustment (see note)",
    "disputed": "No — this doesn't match what I saw",
    "pending": "Haven't reviewed yet",
}


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Member:
    id: str
    name: str
    role: str = ""

    @staticmethod
    def create(name: str, role: str = "") -> "Member":
        return Member(id=_new_id("m"), name=name.strip(), role=role.strip())


@dataclass
class Project:
    """A bounded piece of work — a competition, a quarter, a product launch.
    Contributions are scoped to a project so resume cards are meaningful."""
    id: str
    name: str
    description: str = ""
    status: str = "active"     # active | completed | archived
    started_on: str = ""
    completed_on: str = ""

    @staticmethod
    def create(name: str, description: str = "") -> "Project":
        return Project(id=_new_id("proj"), name=name.strip(),
                       description=description.strip(),
                       started_on=date.today().isoformat())


@dataclass
class Contribution:
    """One deliverable logged by a team member. Append-only.

    Deliberately tracks *what was delivered*, not hours. A contribution
    can optionally reference a workstream or rock from Team OS (free-text,
    no hard dependency)."""
    id: str
    member_id: str
    member_name: str           # denormalized for display + export durability
    project_id: str
    title: str                 # "Built the login page", "Wrote the pitch deck"
    description: str = ""
    category: str = ""         # free-text: Build, Design, Research, Organize, etc.
    logged_on: str = ""
    workstream: str = ""       # optional — matches Team OS workstream name
    rock: str = ""             # optional — matches Team OS rock title

    @staticmethod
    def create(member_id: str, member_name: str, project_id: str,
               title: str, description: str = "", category: str = "",
               workstream: str = "", rock: str = "") -> "Contribution":
        return Contribution(
            id=_new_id("c"), member_id=member_id, member_name=member_name,
            project_id=project_id, title=title.strip(),
            description=description.strip(), category=category.strip(),
            logged_on=date.today().isoformat(),
            workstream=workstream.strip(), rock=rock.strip(),
        )


@dataclass
class Confirmation:
    """A peer's yes/no/adjust on a specific contribution. Append-only.

    One confirmation per reviewer per contribution. The reviewer cannot
    confirm their own contribution."""
    id: str
    contribution_id: str
    reviewer_id: str
    reviewer_name: str
    status: str = "pending"    # confirmed | adjusted | disputed | pending
    note: str = ""
    reviewed_on: str = ""

    @staticmethod
    def create(contribution_id: str, reviewer_id: str,
               reviewer_name: str) -> "Confirmation":
        return Confirmation(id=_new_id("cf"), contribution_id=contribution_id,
                            reviewer_id=reviewer_id,
                            reviewer_name=reviewer_name)


# ── Serialization helpers ─────────────────────────────────────────────────────

def member_from_dict(d: Dict) -> Member:
    return Member(id=d["id"], name=d["name"], role=d.get("role", ""))


def project_from_dict(d: Dict) -> Project:
    return Project(id=d["id"], name=d["name"],
                   description=d.get("description", ""),
                   status=d.get("status", "active"),
                   started_on=d.get("started_on", ""),
                   completed_on=d.get("completed_on", ""))


def contribution_from_dict(d: Dict) -> Contribution:
    return Contribution(
        id=d["id"], member_id=d["member_id"], member_name=d["member_name"],
        project_id=d["project_id"], title=d["title"],
        description=d.get("description", ""), category=d.get("category", ""),
        logged_on=d.get("logged_on", ""),
        workstream=d.get("workstream", ""), rock=d.get("rock", ""),
    )


def confirmation_from_dict(d: Dict) -> Confirmation:
    return Confirmation(
        id=d["id"], contribution_id=d["contribution_id"],
        reviewer_id=d["reviewer_id"], reviewer_name=d["reviewer_name"],
        status=d.get("status", "pending"), note=d.get("note", ""),
        reviewed_on=d.get("reviewed_on", ""),
    )
