# Product backlog

The original estimates are retained as initial estimates, not actual velocity. Sprint completion requires passing acceptance checks, review and integration.

| Sprint | Stories (points) |
| --- | --- |
| 1 | US1 registration (3); US2 login/logout (3); US3 profile (2); US4 add skills (3); US5 edit/remove skills (2); US6 projects (2); US7 certifications (2); US8 opportunities (3); US9 required skills (5); US10 skill catalogue (2). Total: 27. |
| 2 | US11 browse/search (3); US12 filters (3); US13 weighted matching (8); US14 explanations (5); US15 applications (3); US16 applicant view (2); US17 ranking (5). Total: 29. |
| 3 | US18 withdrawal (2); US19 shortlisting (3); US20 application status (2); US21 recommendations (5); US22 skill suggestions (3); US23 notifications (3); US24 team gaps (5); US25 reports (3); US26 moderation (2); US27 deadline closure (2); US28 completeness (2). Total: 32. |

Sprint 1 acceptance: users can register only as student or faculty and authenticate; students manage their own profile, skills (levels 1-4), projects and certifications; faculty manage their own opportunities and unique required skills (levels 1-4, weights 1-100); administrators manage a case-insensitively unique, deactivatable skill catalogue. Protected actions require the correct role and ownership.

## Sprint 2 acceptance criteria (US11-US17)

| Story | Acceptance criteria |
| --- | --- |
| US11 Browse and search (3) | Authenticated users can browse open opportunities in pages of nine. A trimmed, case-insensitive search matches title, description or required skill names without duplicate cards. An empty result state is shown. |
| US12 Filters (3) | Type and active catalogue skill filters combine with search. Selected filters and the trimmed search value remain in pagination links. |
| US13 Weighted matching (8) | A pure Python engine validates levels, weights and unique skill IDs; computes exact fractional credit and contribution points; classifies matched, improvable and missing skills; returns unscored results for no requirements; rounds totals half-up. |
| US14 Fit explanations (5) | Students see the score, a progress indicator, per-skill level/minimum/weight/contribution and status groups on detail pages. Students without skills see missing requirements and a link to add skills. Faculty see requirements; owners can open the applicant list. |
| US15 Apply (3) | Only students can apply through CSRF-protected POST to open opportunities. A student can apply once per opportunity; duplicate, closed, expired and draft attempts are safely handled. The detail page shows Apply, Applied with date, or Applications closed as appropriate. |
| US16 Applicant view (2) | Only the owning faculty member can view applicants. The list includes name, branch/year, interests, skills, projects and certifications, with related data loaded in batches. |
| US17 Ranking (5) | Applicant scores are calculated from current profiles and sorted by score descending, earlier application time, case-insensitive applicant name and stable application ID. Unscored entries follow scored entries; each score can expand to a per-skill breakdown. |

The open rule is published status with a deadline on or after the configured local date. Expired records are not automatically closed in Sprint 2. Sprint 3 remains pending.

## Human records

- Planning poker and team decisions: pending.
- Daily Scrum: pending.
- Review and retrospective: pending.
- Burndown, velocity and pairing: pending actual team records.

Definition of Done: acceptance criteria satisfied, security and relevant tests pass, application verified, changes reviewed and integrated. Human-dependent records require actual team input; none are asserted here.
