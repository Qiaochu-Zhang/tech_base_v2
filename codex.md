# Agent Rules (Codex)

This project follows a staged development approach:

- V1.5 = Frontend prototype (static HTML + localStorage)
- V1.6+ = Backend (FastAPI) + PostgreSQL + Docker

Rules differ by stage. You must detect the current stage before acting.

---

# 1. Scope Control

- Only work on the current Block specified in TASKS.md.
- Execute Blocks strictly in order.
- Do NOT modify other Blocks.
- Do NOT refactor unrelated code.
- Do NOT introduce new architecture unless the current Block requires it.

---

# 2. Frontend Protection (IMPORTANT)

Current repository structure:

Root directory contains:
- index.html
- upload_review.html
- info_table.html
- info_detail.html
- drafts.html
- dashboard.html
- excel_import.html

These files form the confirmed frontend baseline.

Rules:

- Treat all existing HTML files as stable UI.
- Only modify them if the current Block explicitly requires logic integration.
- Keep diffs minimal and localized.
- Do NOT redesign UI.
- Do NOT rename existing IDs, data fields, or page structure unless required by spec.md.

---

# 3. Backend & Data Model Rules

- spec.md is the single source of truth for:
  - field names
  - enums
  - state machine
  - publish rules
- Never rename database fields defined in spec.md.
- Never introduce new states unless explicitly required.
- Never change draft → ai_suggested → published flow.

---

# 4. Stage-Aware Verification Rules

## Stage A – Frontend Prototype (No Docker Yet)

If the repository does NOT contain:

- docker-compose.yml
- backend directory
- FastAPI app

Then:

- Do NOT attempt to run docker commands.
- Validate using static server:

  python3 -m http.server 8000

- Verification is manual via browser testing.
- Ensure:
  - No console errors
  - localStorage persists correctly
  - published items appear in table
  - draft items do NOT appear in table

---

## Stage B – Backend + Docker Stage

If docker-compose.yml exists:

You must run before finishing:

- docker compose up -d --build
- docker compose run --rm api pytest -q
- docker compose run --rm web npm run build

All must pass before declaring completion.

If tests fail:
- Fix
- Rerun
- Do not ignore failures

---

# 5. Commit Rules

- Never commit directly to main.
- Always work on a feature branch.
- Small incremental commits (1–3 per Block).
- Clear commit messages:
  - feat:
  - fix:
  - refactor:
- Never commit secrets (.env, keys, credentials).

---

# 6. Output Format After Completing a Block

You must output:

1) Files changed
2) What was modified and why
3) How to verify (commands + click path)
4) Any assumptions made

Do not declare completion without verification.

---

# 7. Safety Constraints

- Do not delete existing working features.
- Do not silently change data structure.
- Do not migrate storage method unless the current Block explicitly requires it.
- Do not introduce new dependencies unless strictly necessary.

---

# 8. Human Control

- Human review is mandatory before merge.
- Do not auto-merge.
- Wait for explicit human confirmation before moving to next Block.