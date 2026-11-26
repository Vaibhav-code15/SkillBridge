# Project conventions

Use Django 5.2, Python 3.14, Django templates, vanilla JavaScript and the Tailwind CLI. Keep views thin, validate input server-side, enforce roles and object ownership, and commit migrations. Never commit credentials or local databases.

Run Django checks, migration checks, Ruff and pytest before requesting review. Use `npm.cmd` in PowerShell when the npm script is blocked by execution policy.

Keep main stable. Do not rewrite published history. Record only real collaboration and test evidence. Ask for explicit approval before merges, tags, releases or changes to remote project settings.

## Current sprint

Maintain the Sprint 1–3 implementation and its genuine TDD history. The current work is post-Sprint-3 product experience refinement by Vaibhav; do not add or renumber user stories. Merge only after successful CI, required human review, and explicit approval.

## Design system

Use midnight navy and deep indigo navigation and hero surfaces, pearl backgrounds, violet and indigo primary actions, and category accents: violet for internships, blue for research, and teal for academic projects. Use local Inter and Plus Jakarta Sans fonts, visible focus indicators, reduced-motion support, and real application data. See `docs/DESIGN_SYSTEM.md`.
