# Project conventions

Use Django 5.2, Python 3.14, Django templates, vanilla JavaScript and the Tailwind CLI. Keep views thin, validate input server-side, enforce roles and object ownership, and commit migrations. Never commit credentials or local databases.

Run Django checks, migration checks, Ruff and pytest before requesting review. Use `npm.cmd` in PowerShell when the npm script is blocked by execution policy.

Keep main stable. Do not rewrite published history. Record only real collaboration and test evidence. Ask for explicit approval before merges, tags, releases or changes to remote project settings.

## Current sprint

Implement Sprint 2 only (US11-US17, 29 points), by Sarah Abbas. Do not implement Sprint 3. The owner has authorised Sprint 2 commits, pushes, and TDD phase transitions in advance. Preserve separate RED–GREEN–REFACTOR commits and CI runs. Merge only after successful CI and required human review.
