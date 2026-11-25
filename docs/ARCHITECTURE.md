# Architecture

Django templates and vanilla JavaScript render server-side forms and role-specific dashboards. `accounts` owns the Sprint 1 domain models and views, the Sprint 2 `Application` model and workflow, and thin ORM adapters in `accounts.matching`. The independent `matching` package contains only frozen dataclasses and pure Python scoring and ranking functions; it has no Django or HTTP dependency. `skills.services` checks catalogue names. Server-side role and object ownership checks protect changes. SQLite is used locally; settings support PostgreSQL but it has not been verified.

```mermaid
erDiagram
  User ||--o| StudentProfile : has
  User ||--o{ StudentSkill : owns
  Skill ||--o{ StudentSkill : describes
  User ||--o{ Project : owns
  User ||--o{ Certification : owns
  User ||--o{ Opportunity : posts
  Opportunity ||--o{ RequiredSkill : requires
  Skill ||--o{ RequiredSkill : describes
  User ||--o{ Application : submits
  Opportunity ||--o{ Application : receives
```

## Matching formula

For each required skill, the student's proficiency `s` is zero when absent, the minimum level is `m` (1-4), and the requirement weight is `w` (1-100 in the database). A skill is matched when `s >= m` with credit 1, improvable when `0 < s < m` with credit `s/m`, and missing when `s == 0` with credit 0. Input validation rejects levels outside 0-4, minimums outside 1-4, non-positive weights, and duplicate skill IDs.

The overall score is `100 * sum(w * credit) / sum(w)`, calculated with `fractions.Fraction` and rounded to an integer with half-up rounding. An opportunity without requirements is unscored (`None`). Each skill contribution is the exact fraction `100 * w * credit / sum(w)` and is displayed to one decimal place. Displayed contributions can differ from the rounded integer total only because of rounding.

Worked example: two equally weighted skills, one matched and one at level 1 with a minimum of 4, produce credits 1 and 1/4. The total is `100 * (1 + 1/4) / 2 = 62.5`, rounded half-up to 63. The displayed contributions are 50.0 and 12.5 points.

Ranked applicants sort by score descending, then earlier application time, case-insensitive applicant name, and stable application ID. Unscored applicants appear after scored applicants.

## Opportunity availability and applications

`Opportunity.objects.is_open()` and `Opportunity.is_open` use the same rule: status is published and the deadline is today or later according to Django's configured local date. Applications remain open through the deadline date. Expired opportunities are not automatically closed. `Application` records one student/opportunity pair, an applied status and an explicit timestamp; database uniqueness and indexes support duplicate protection and applicant retrieval.

Proficiency is 1-4, and requirement weights are 1-100. Database constraints protect ranges and uniqueness. Matching is computed from current student skills when discovery, detail, and applicant pages render.
