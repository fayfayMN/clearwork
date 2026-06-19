# 🔍 Clearwork

Track who did what, confirm it with peers, and turn the record into
**verified proof of contribution** — a resume card that's more credible
than a self-reported bullet point.

The **PROVE** stage that completes the product loop:

```
TeamUp (FORM) → Team OS (RUN) → Clearwork (PROVE)
```

**Open the app** → `streamlit run app.py`

---

## How to use it

### Step 1 — Team Setup

Add team members and create a project (any bounded piece of work — a
hackathon, a quarter, a product launch).

### Step 2 — Log contributions

Each person logs what they *delivered*. Not hours — deliverables. "Built
the login page" not "worked 8 hours." This is what peers can verify and
what a resume card can show.

### Step 3 — Peer confirmation

Each teammate reviews others' contributions: **confirmed** (yes, this
happened), **adjusted** (partly, with a note), or **disputed** (no, this
doesn't match what I saw). You can't confirm your own work — that's the
whole point.

### Step 4 — Balance view

See if contributions are distributed fairly. The app flags heroes (one
person doing > 50%), ghosts (zero contributions), low confirmation rates,
and disputed claims.

### Step 5 — Resume card

Generate a verified project card for any member. Each contribution shows
its peer confirmation status. Download as Markdown for LinkedIn, a
portfolio, or a job application.

---

## What's in v1

| Page | What it does |
|------|--------------|
| **Team Setup** | Members + projects with lifecycle status |
| **Log** | Log deliverables with category, workstream, and rock links |
| **Confirm** | Peer review — confirm / adjust / dispute with notes |
| **Balance** | Contribution distribution + health check (hero / ghost / disputed) |
| **Resume Card** | Verified project card, downloadable as Markdown |

## Design principles

- **Deliverables, not hours.** Hours invite gaming; deliverables invite accountability.
- **Peer confirmation, not manager ratings.** Yes/no/adjust, not 1-5 stars.
- **Append-only records.** Contributions and confirmations can't be edited or deleted.
- **Deterministic analysis.** Balance checks are pure Python — free, explainable.
- **No API key, no cost.** Data persists to `clearwork_state.json`.

## Run locally

```bash
cd clearwork
pip install -r requirements.txt
streamlit run app.py
```

Click **Load demo project** to see a sample hackathon with mixed
confirmation states (confirmed, adjusted, disputed, pending).
