# Agent Rules (Codex)

## 1. Scope Control
- Only work on the current Block specified in CODEX_TASKS.md.
- Do not modify other Blocks.
- Do not refactor unrelated code.

## 2. Frontend Protection
- Treat `frontend/` as stable baseline UI.
- Only modify it when explicitly required.
- Keep diffs minimal and localized.

## 3. Backend Development Rules
- Follow spec.md for field names and enums.
- Do not rename database fields.
- Do not introduce new states unless requested.

## 4. Required Commands Before Finishing
You must run:

- `docker compose up -d --build`
- `docker compose run --rm api pytest -q`
- `docker compose run --rm web npm run build`

All must pass before declaring completion.

## 5. Commit Rules
- Small incremental commits (1–3 per Block)
- Clear commit messages
- Never commit secrets (.env, keys)

## 6. If Tests Fail
- Fix the issue
- Rerun until green
- Do not ignore failing tests

## 7. Output Format
After finishing a Block, output:
- Files changed
- What was modified
- How to verify

## 8. Git Rules
- Never commit directly to main.
- Work on a feature branch.
- Human must review before merge.