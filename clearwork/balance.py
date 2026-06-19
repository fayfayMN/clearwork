"""Contribution balance — deterministic, explainable analysis.

Not a leaderboard. The point is to answer "is work distributed fairly?"
and to surface imbalances early enough to fix them, not to rank people.

Signals:
  - Distribution: what % of total contributions each person logged
  - Confirmation rate: what % of a person's contributions are peer-confirmed
  - Coverage: which categories/workstreams have no contributions at all
  - Hero risk: one person logging > 50% of all contributions
  - Ghost risk: a member with zero contributions

No LLM. Every finding is a transparent rule with a stated threshold.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List


HERO_THRESHOLD = 0.50      # one person > 50% of contributions
GHOST_THRESHOLD = 0        # zero contributions


def analyze(members: List, contributions: List, confirmations: List,
            project_id: str | None = None) -> Dict:
    """Return {per_member: [...], findings: [...], summary: str}.

    Optionally filter to a single project.
    """
    contribs = contributions
    if project_id:
        contribs = [c for c in contribs if c.project_id == project_id]

    confirms = confirmations
    if project_id:
        contrib_ids = {c.id for c in contribs}
        confirms = [cf for cf in confirms if cf.contribution_id in contrib_ids]

    findings: List[Dict] = []
    total = len(contribs)

    if total == 0:
        return {"per_member": [], "findings": [
            {"level": "warn", "msg": "No contributions logged yet."}],
            "summary": "Nothing to analyze."}

    # ── Per-member stats ──────────────────────────────────────────────────────
    by_member: Dict[str, List] = {m.id: [] for m in members}
    for c in contribs:
        by_member.setdefault(c.member_id, []).append(c)

    confirm_status: Dict[str, List[str]] = {}
    for cf in confirms:
        confirm_status.setdefault(cf.contribution_id, []).append(cf.status)

    per_member = []
    for m in members:
        mine = by_member.get(m.id, [])
        count = len(mine)
        pct = round(count / total * 100) if total else 0

        confirmed = 0
        reviewed = 0
        for c in mine:
            statuses = confirm_status.get(c.id, [])
            non_pending = [s for s in statuses if s != "pending"]
            if non_pending:
                reviewed += 1
                if all(s == "confirmed" for s in non_pending):
                    confirmed += 1

        confirm_rate = round(confirmed / reviewed * 100) if reviewed else None
        categories = sorted(set(c.category for c in mine if c.category))

        per_member.append({
            "id": m.id, "name": m.name, "count": count, "pct": pct,
            "confirmed": confirmed, "reviewed": reviewed,
            "confirm_rate": confirm_rate, "categories": categories,
        })

    # ── Findings ──────────────────────────────────────────────────────────────
    for pm in per_member:
        if pm["count"] == GHOST_THRESHOLD:
            findings.append({"level": "warn",
                             "msg": f"**{pm['name']}** has zero contributions logged — "
                                    "invisible work or disengagement?"})
        if pm["pct"] > HERO_THRESHOLD * 100:
            findings.append({"level": "warn",
                             "msg": f"**{pm['name']}** logged {pm['pct']}% of all "
                                    "contributions — hero risk / bus factor."})
        if pm["confirm_rate"] is not None and pm["confirm_rate"] < 50:
            findings.append({"level": "warn",
                             "msg": f"**{pm['name']}** has a low confirmation rate "
                                    f"({pm['confirm_rate']}%) — peers aren't fully "
                                    "confirming their logged work."})

    # Category coverage
    all_cats = set(c.category for c in contribs if c.category)
    member_cats = {m.id: set(c.category for c in by_member.get(m.id, []) if c.category)
                   for m in members}
    uncovered = all_cats - set().union(*member_cats.values()) if member_cats else set()
    if uncovered:
        findings.append({"level": "warn",
                         "msg": f"No contributions in: {', '.join(sorted(uncovered))}"})

    # Disputed contributions
    disputed = [c for c in contribs
                if any(s == "disputed" for s in confirm_status.get(c.id, []))]
    if disputed:
        findings.append({"level": "error",
                         "msg": f"{len(disputed)} contribution(s) disputed by peers — "
                                "resolve before closing the project."})

    if not findings:
        findings.append({"level": "ok",
                         "msg": "Contributions are balanced and confirmed."})

    errors = sum(1 for f in findings if f["level"] == "error")
    warns = sum(1 for f in findings if f["level"] == "warn")
    if errors:
        summary = f"{errors} issue(s) to resolve."
    elif warns:
        summary = f"Generally balanced; {warns} thing(s) worth checking."
    else:
        summary = "Healthy and balanced."

    return {"per_member": per_member, "findings": findings, "summary": summary}
