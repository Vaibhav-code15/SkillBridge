# Sprint 2: Intelligent Matching and Applications

Scope: US11-US17, 29 initial story points. This work is on `feature/sprint2-intelligent-matching` and is pending human review and integration. No Sprint 3 stories are included.

## Delivered in this branch

- Opportunity discovery with nine-item pagination, case-insensitive search, and combined type and active-skill filters.
- Pure Python weighted skill scoring with exact fractions, explicit matched/improvable/missing results, half-up rounding, and deterministic ranking.
- Student fit details and single-application POST flow with role, CSRF, deadline and duplicate protections.
- Faculty applicant details and live ranked scores for opportunities owned by the viewing faculty member.
- Idempotent fictional demo applications with varied profiles and a same-score/time tie for the name and ID tie-breaks.

## Evidence

The RED, GREEN and REFACTOR commits and their observed workflow results are recorded in [TDD evidence](../TDD.md). Automated checks and CI runs are reported from their actual results in the pull request description. No screenshot is included unless captured during browser verification.

## Human records

- Planning poker and team decisions: pending team input.
- Daily Scrum: pending team input.
- Review and retrospective: pending team input.
- Burndown, velocity, pairing and contributions: pending actual team records.
- Human review and merge: pending.

## Remaining manual verification

- The automated browser UI session did not start, so no screenshots were captured. Review all three pages at desktop and mobile widths:
  - Discovery: verify card layout, combined search/type/skill filters, nine-item pagination and empty state.
  - Detail: verify fit score, proficiency segments and skill groups; inspect Apply, Applied with date, closed and no-skills states.
  - Applicants: verify ranked profile cards, expandable skill breakdowns and usable vertical scrolling on narrow screens.
- Review the pull request and approve integration after CI passes.
- Verify PostgreSQL configuration and production settings before deployment.
