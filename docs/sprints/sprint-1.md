# Sprint 1 record

Scope: US1–US10, 27 initial story points. See the backlog and TDD evidence for details. Completion, velocity and release status are pending review and integration.

## Human records

- Planning poker and team decisions: pending.
- Daily Scrum: pending.
- Review and retrospective: pending.
- Burndown, velocity and pairing: pending actual team records.

## Remaining verification and integration

- Verify desktop and mobile layouts in a working browser; capture genuine screenshots. Computer-use connection was unavailable in this session.
- Verify PostgreSQL configuration and production settings before any deployment claim.
- Review the implementation, confirm all story acceptance criteria and integrate only after human review and passing remote CI.
- Confirm the username-based login choice against the earlier email-based plan; registration collects email but authentication currently uses username.

## Acceptance checklist

| Story | Acceptance check | Evidence / status |
| --- | --- | --- |
| US1 | Students and faculty register; privileged registration is rejected. | Student/faculty registration and privilege-escalation tests; direct faculty signup has no institutional verification. |
| US2 | Users can sign in and sign out. | Authentication workflow test; username-based, not email-based. |
| US3 | Students can update branch, year and interests. | Profile update test. |
| US4–US5 | Students add, edit and remove their own skills, with levels 1–4. | Add, edit, remove, invalid-level and ownership tests. |
| US6–US7 | Students manage their own projects and certifications. | Creation, edit and removal tests. |
| US8 | Faculty create and manage their own typed opportunities, deadlines and statuses. | Create, edit, delete and cross-owner denial tests. |
| US9 | Faculty manage unique required skills with minimum level 1–4 and weight 1–100. | Create, edit, remove, invalid range, duplicate and ownership tests. |
| US10 | Administrators add, rename and deactivate catalogue skills with case-insensitive uniqueness. | Add, rename, deactivate, duplicate and role-denial tests. |
