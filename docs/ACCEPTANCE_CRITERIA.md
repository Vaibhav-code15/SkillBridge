# SkillBridge acceptance criteria and traceability

## Introduction and purpose

This record supports the R2 evaluation of the 28 original backlog items for Vaibhav Khandelwal and Sarah Abbas. The initial estimates total **88 points**: 27 in Sprint 1, 29 in Sprint 2 and 32 in Sprint 3. Estimates are not actual velocity.

The backlog records titles and estimates, but not full original As a / I want / So that statements. The statements below are reconstructed from those records, not verbatim historical quotations. The acceptance checks describe the merged application; the scenarios specify behaviour and are not claimed as automated tests unless supported by the named test. A cited test may cover only part of a criterion. “Implemented” describes repository evidence, not human acceptance. Manual checks and R2 approval remain open until a reviewer records actual outcomes.

Username-based authentication, faculty self-registration without institutional verification, owner-only faculty browsing, and deadline closure on visits or via a command are implementation decisions, not evidence of additional original requirements. Application notes and private resume sharing are post-Sprint-3 enhancements, separate from US1–US28. Historical sprint records may describe an earlier pending-review state. See [AGILE.md](AGILE.md), the sprint records and [TDD.md](TDD.md); existing TDD evidence is unchanged.

## Sprint 1: US1–US10

### US1: Student and faculty registration — 3 points

**Story:** As a prospective student or faculty member, I want to register in my role, so that I can use the appropriate workspace.

**Criteria:** Valid student and faculty registrations create accounts and sign the user in; student signup creates a profile. Invalid roles are rejected and submitted privilege flags cannot create an administrator. Faculty affiliation is not verified.

- **Positive:** Given valid student or faculty details, when a visitor registers, then an account with the selected role is created.
- **Negative:** Given an invalid role or privilege flag, when registration is submitted, then no administrator access is granted.

**Implementation:** `accounts/views.py::register`, `accounts/forms.py::RegistrationForm`, `accounts/models.py::User, StudentProfile`. **Frontend:** `templates/registration/register.html`. **Tests:** `tests/test_workflows.py::test_registration_login_and_role_escalation`, `test_faculty_registration_and_invalid_role`. **Status:** Implemented; cited tests cover representative cases. Manually review validation and faculty enrolment policy; human acceptance is not recorded.

### US2: Login and logout — 3 points

**Story:** As a registered user, I want to sign in and out, so that I can use my account securely.

**Criteria:** Active users sign in using username and password; logout uses POST. Invalid credentials or an inactive account cannot establish an authenticated session.

- **Positive:** Given an active account and valid credentials, when the user signs in, then they can access their dashboard.
- **Negative:** Given invalid credentials or an inactive account, when login is attempted, then access is denied.

**Implementation:** `config/urls.py`, `accounts/forms.py::SkillBridgeAuthenticationForm`, `accounts/views.py::dashboard`. **Frontend:** `templates/registration/login.html`, `templates/base.html`. **Tests:** `tests/test_workflows.py::test_registration_login_and_role_escalation`, `tests/test_sprint3_moderation.py::test_admin_user_moderation_and_inactive_sessions`. **Status:** Implemented; manually verify login errors and logout in a browser. Human acceptance is not recorded.

### US3: Student profile — 2 points

**Story:** As a student, I want to maintain my academic profile, so that I can present my background and interests.

**Criteria:** A student can update their own branch, academic year and interests. Year, if supplied, is 1–8. Student role and signed-in ownership are enforced.

- **Positive:** Given valid academic details, when a student saves their profile, then their own details are updated.
- **Negative:** Given an invalid year or non-student viewer, when an update is attempted, then validation or role checks prevent it.

**Implementation:** `accounts/views.py::profile_edit, profile_overview`, `accounts/forms.py::ProfileForm`, `accounts/models.py::StudentProfile`. **Frontend:** `templates/form.html`, `templates/profile_overview.html`. **Tests:** `tests/test_workflows.py::test_student_portfolio_and_ownership`. **Status:** Implemented; the test covers the valid update. Manually verify invalid year and role denial; human acceptance is not recorded.

### US4: Add student skills — 3 points

**Story:** As a student, I want to add catalogue skills and proficiency, so that I can show my strengths.

**Criteria:** A student adds an active catalogue skill with proficiency 1–4; duplicate student/skill entries and invalid levels are rejected.

- **Positive:** Given an active skill and level 1–4, when the student saves it, then it is added to their profile.
- **Negative:** Given a duplicate or level outside 1–4, when it is submitted, then validation rejects it.

**Implementation:** `accounts/views.py::student_item`, `accounts/forms.py::StudentSkillForm`, `accounts/models.py::StudentSkill`. **Frontend:** `templates/form.html`, `templates/dashboard.html`, `templates/profile_overview.html`. **Tests:** `tests/test_workflows.py::test_student_portfolio_and_ownership`. **Status:** Implemented; manually check form errors and empty state. Human acceptance is not recorded.

### US5: Edit and remove student skills — 2 points

**Story:** As a student, I want to edit or remove my skills, so that my portfolio stays current.

**Criteria:** Owners can edit and remove their skills; the 1–4 and uniqueness constraints remain enforced. Other students' records are inaccessible; deletion requires POST.

- **Positive:** Given an owned skill, when its level is changed or removal is submitted, then the record is updated or removed.
- **Negative:** Given a foreign skill or a GET deletion request, when the request is made, then the record is unchanged.

**Implementation:** `accounts/views.py::student_item, student_delete`, `accounts/forms.py::StudentSkillForm`, `accounts/models.py::StudentSkill`. **Frontend:** `templates/form.html`, `templates/dashboard.html`, `templates/profile_overview.html`. **Tests:** `tests/test_workflows.py::test_student_portfolio_and_ownership`, `test_edit_and_remove_sprint_one_records`. **Status:** Implemented; manually check confirmation and keyboard access. Human acceptance is not recorded.

### US6: Student projects — 2 points

**Story:** As a student, I want to maintain projects in my portfolio, so that I can show my work.

**Criteria:** Owners can create, edit and remove projects with title, description and optional URL. The student role, ownership and URL validation apply.

- **Positive:** Given valid project details, when a student saves, edits or removes their project, then their portfolio reflects the change.
- **Negative:** Given a foreign project or invalid form data, when a change is submitted, then access or validation prevents it.

**Implementation:** `accounts/views.py::student_item, student_delete`, `accounts/forms.py::ProjectForm`, `accounts/models.py::Project`. **Frontend:** `templates/form.html`, `templates/dashboard.html`, `templates/profile_overview.html`. **Tests:** `tests/test_workflows.py::test_student_portfolio_and_ownership`, `test_edit_and_remove_sprint_one_records`. **Status:** Implemented; manually verify project-specific cross-owner and invalid URL cases. Human acceptance is not recorded.

### US7: Student certifications — 2 points

**Story:** As a student, I want to maintain my certifications, so that I can show my learning.

**Criteria:** Owners can add, edit and remove certification title and issuer, with optional date and URL; date, URL, student role and ownership are validated.

- **Positive:** Given a valid certification, when the student saves, edits or removes it, then their portfolio is updated.
- **Negative:** Given a foreign record or invalid date or URL, when a change is attempted, then access or validation prevents it.

**Implementation:** `accounts/views.py::student_item, student_delete`, `accounts/forms.py::CertificationForm`, `accounts/models.py::Certification`. **Frontend:** `templates/form.html`, `templates/dashboard.html`, `templates/profile_overview.html`. **Tests:** `tests/test_workflows.py::test_student_portfolio_and_ownership`, `test_edit_and_remove_sprint_one_records`. **Status:** Implemented; manually verify certification-specific ownership and invalid field cases. Human acceptance is not recorded.

### US8: Faculty opportunities — 3 points

**Story:** As a faculty member, I want to create and manage opportunities, so that students can find suitable work.

**Criteria:** Faculty create and edit their own opportunities with title, description, type, deadline and status. Foreign owners are denied. Deletion is POST-only and is blocked when applications exist, preserving history.

- **Positive:** Given an owned opportunity without applications, when the owner creates, edits or deletes it, then the requested change is saved.
- **Negative:** Given another faculty member's opportunity or one with applications, when deletion is attempted, then the operation is denied or the record remains.

**Implementation:** `accounts/views.py::opportunity_edit, opportunity_delete`, `accounts/forms.py::OpportunityForm`, `accounts/models.py::Opportunity`, `accounts/services.py::delete_empty_opportunity`. **Frontend:** `templates/form.html`, `templates/opportunity.html`, `templates/dashboard.html`. **Tests:** `tests/test_workflows.py::test_faculty_requirements_and_ownership`, `test_edit_and_remove_sprint_one_records`; `tests/test_sprint3_lifecycle.py::test_removed_and_hard_delete_preserve_application`. **Status:** Implemented; manually review form error states. Human acceptance is not recorded.

### US9: Required skills, levels and weights — 5 points

**Story:** As a faculty owner, I want to define required skills and their minimum levels and weights, so that an opportunity's needs are clear.

**Criteria:** Owners add, edit and remove requirements. Each skill is unique per opportunity, proficiency is 1–4 and weight is 1–100. Ownership is enforced; deletion requires POST.

- **Positive:** Given a unique skill, valid minimum and weight, when the owner saves it, then the requirement belongs to the opportunity.
- **Negative:** Given a duplicate, out-of-range value or foreign opportunity, when submitted, then validation or ownership checks prevent the change.

**Implementation:** `accounts/views.py::requirement_edit, requirement_delete`, `accounts/forms.py::RequiredSkillForm`, `accounts/models.py::RequiredSkill`. **Frontend:** `templates/form.html`, `templates/opportunity.html`. **Tests:** `tests/test_workflows.py::test_faculty_requirements_and_ownership`, `test_edit_and_remove_sprint_one_records`. **Status:** Implemented; manually verify cross-owner edit and delete controls. Human acceptance is not recorded.

### US10: Administrator skill catalogue — 2 points

**Story:** As an administrator, I want to manage the skill catalogue, so that skill names remain consistent.

**Criteria:** A superuser can add, rename and deactivate skills. Names are nonblank and unique ignoring case; non-administrators are denied.

- **Positive:** Given a distinct skill name, when an administrator saves it, then the catalogue contains it.
- **Negative:** Given a duplicate differing only in case or a non-administrator, when management is attempted, then validation or permissions prevent the change.

**Implementation:** `accounts/views.py::catalogue_edit`, `accounts/forms.py::SkillForm.clean_name`, `accounts/models.py::Skill`, `skills/services.py::skill_name_exists`. **Frontend:** `templates/form.html`, `templates/dashboard.html`. **Tests:** `tests/test_workflows.py::test_admin_catalogue_and_constraints`, `test_edit_and_remove_sprint_one_records`; `tests/test_skill_names.py::test_duplicate_skill_name_is_case_insensitive`. **Status:** Implemented; manually inspect catalogue feedback. Human acceptance is not recorded.

## Sprint 2: US11–US17

### US11: Browse and search opportunities — 3 points

**Story:** As a student or faculty member, I want to browse and search open opportunities, so that I can find relevant work.

**Criteria:** Open means visible, published and deadline on or after the configured local date. Results are paginated nine per page; trimmed case-insensitive search covers title, description and required skill. Faculty browse only their own opportunities.

- **Positive:** Given an authorised user and matching open opportunities, when they search, then matching results appear without duplicate cards.
- **Negative:** Given no match or a foreign faculty opportunity, when results are requested, then the empty state appears or the foreign opportunity is excluded.

**Implementation:** `accounts/views.py::opportunity_list`, `accounts/models.py::OpportunityQuerySet.is_open, Opportunity.is_open`. **Frontend:** `templates/opportunity_list.html`, `templates/partials/opportunity_card.html`. **Tests:** `tests/test_matching_workflows.py::test_search_filters_and_pagination_keep_query_state`, `test_faculty_browse_excludes_other_faculty_opportunities`, `test_open_boundary_uses_local_date_for_property_and_queryset`. **Status:** Implemented; manually check pagination and mobile empty states. Human acceptance is not recorded.

### US12: Opportunity filters — 3 points

**Story:** As a student or faculty member, I want to combine type and skill filters with search, so that I can narrow results.

**Criteria:** Valid type and active-skill filters combine with search; selection and trimmed search are preserved in pagination. Invalid filter values are ignored.

- **Positive:** Given valid search, type and skill values, when filters are applied, then results meet the combined criteria.
- **Negative:** Given invalid values or no matches, when the user filters, then invalid selections are ignored or an empty state is shown.

**Implementation:** `accounts/views.py::opportunity_list`, `accounts/templatetags/querystring.py`. **Frontend:** `templates/opportunity_list.html`. **Tests:** `tests/test_matching_workflows.py::test_search_filters_and_pagination_keep_query_state`. **Status:** Implemented; manually check invalid filters and keyboard use. Human acceptance is not recorded.

### US13: Weighted skill matching — 8 points

**Story:** As a student, I want to see a weighted skill match, so that I can understand my suitability.

**Criteria:** The engine uses exact fractional proficiency credit and weights, then rounds half-up. Missing skills score zero; no requirements is unscored. Duplicate requirement IDs, invalid minimums, weights or student levels are rejected.

- **Positive:** Given valid weighted requirements and levels, when matching runs, then the score and classifications follow the weighted formula.
- **Negative:** Given no requirements or invalid inputs, when matching runs, then the result is unscored or validation raises an error.

**Implementation:** `matching/__init__.py::calculate_match, _classify_skill, _round_half_up`, `accounts/matching.py::match_student, requirements_for, skill_levels_for`. **Frontend:** `templates/opportunity.html`, `templates/partials/score_ring.html`. **Tests:** `tests/test_matching_engine.py::test_weights_change_the_overall_result`, `test_empty_requirements_are_unscored_and_inputs_are_validated`, `test_half_up_rounds_62_point_5_to_63`. **Status:** Implemented; manually compare representative displayed scores. Human acceptance is not recorded.

### US14: Skill fit explanations — 5 points

**Story:** As a student, I want to see how my skills compare with requirements, so that I can understand my match.

**Criteria:** Detail groups matched, improvable and missing skills and shows proficiency, minimum, weight and contribution. No requirements is unscored; students without skills receive an add-skills link. Faculty see requirements; owners can access applicants.

- **Positive:** Given required skills, when a student opens detail, then fit and per-skill comparisons appear.
- **Negative:** Given no requirements or a faculty viewer, when detail loads, then the unscored state or faculty-appropriate view is shown.

**Implementation:** `accounts/views.py::opportunity_detail, match_breakdown, match_rows`, `accounts/matching.py::match_student`. **Frontend:** `templates/opportunity.html`, `templates/partials/fit_skill.html`, `templates/partials/score_ring.html`. **Tests:** `tests/test_matching_workflows.py::test_detail_shows_fit_to_students_and_requirements_only_to_faculty`; `tests/test_matching_engine.py::test_groups_matched_improvable_and_missing_skills`. **Status:** Implemented; manually verify no-requirement and no-skills states and displayed points. Human acceptance is not recorded.

### US15: Apply to opportunities — 3 points

**Story:** As a student, I want to apply to an open opportunity, so that faculty can consider me.

**Criteria:** Only students can apply using CSRF-protected POST. A published visible opportunity is open through its local deadline day. Duplicate, draft, closed and expired attempts cannot create another application.

- **Positive:** Given an open opportunity and no existing application, when a student applies, then one application is recorded.
- **Negative:** Given missing CSRF, a non-student, a closed opportunity or a duplicate, when an application is submitted, then access is denied or no additional record is created.

**Implementation:** `accounts/views.py::opportunity_apply`, `accounts/services.py::apply_to_opportunity`, `accounts/models.py::Application, Opportunity.is_open`. **Frontend:** `templates/opportunity.html`. **Tests:** `tests/test_matching_workflows.py::test_application_post_guards_duplicates_closed_draft_roles_and_csrf`, `test_open_boundary_uses_local_date_for_property_and_queryset`. **Status:** Implemented; manually verify apply, applied and closed states and no-JavaScript submission. Human acceptance is not recorded.

### US16: Faculty applicant view — 2 points

**Story:** As a faculty owner, I want to review my applicants' profiles, so that I can assess candidates.

**Criteria:** Only the owning faculty member can access applicants. The view displays available names, academic details, interests, skills, projects and certifications, with related data prefetched; withdrawn applicants are separated.

- **Positive:** Given active applicants, when their faculty owner opens the list, then available profile details appear.
- **Negative:** Given another faculty member, student or administrator, when the list is requested, then access is denied.

**Implementation:** `accounts/views.py::opportunity_applicants`, `accounts/models.py::Application, StudentProfile`. **Frontend:** `templates/opportunity_applicants.html`. **Tests:** `tests/test_matching_workflows.py::test_applicants_are_ranked_live_and_other_roles_cannot_view`; `tests/test_sprint3_lifecycle.py::test_withdraw_reapply_decisions_and_notification_ownership`. **Status:** Implemented; manually review all profile fields and long-content layout. Human acceptance is not recorded.

### US17: Rank applicants — 5 points

**Story:** As a faculty owner, I want applicants ranked by current skill fit, so that I can compare candidates consistently.

**Criteria:** Scores use current skills. Sort order is descending score, earlier application time, case-insensitive name, then stable application ID; unscored candidates follow scored candidates. The owner can expand skill details.

- **Positive:** Given applicants with scores or ties, when the owner opens rankings, then the documented sorting sequence applies.
- **Negative:** Given a non-owner or an unscored candidate, when the list is requested, then access is denied or unscored candidates follow scored candidates.

**Implementation:** `accounts/views.py::opportunity_applicants`, `accounts/matching.py::match_student`, `matching/__init__.py::rank_candidates`. **Frontend:** `templates/opportunity_applicants.html`, `templates/partials/fit_skill.html`. **Tests:** `tests/test_matching_workflows.py::test_applicants_are_ranked_live_and_other_roles_cannot_view`. **Status:** Implemented; manually check expandable details and verify tie-break coverage beyond the cited test. Human acceptance is not recorded.

## Sprint 3: US18–US28

### US18: Withdraw and reapply — 2 points

**Story:** As a student, I want to withdraw and reapply while an opportunity is open, so that I can manage my participation.

**Criteria:** Owners may withdraw applied or shortlisted applications by POST. A withdrawn application can be reapplied on the same row while open; rejected applications cannot be resubmitted. Other students cannot withdraw it.

- **Positive:** Given an owned applied or shortlisted application, when the student withdraws and reapplies while open, then the same record returns to applied.
- **Negative:** Given a rejected, closed or foreign application, when an invalid withdrawal or reapplication is attempted, then it is rejected.

**Implementation:** `accounts/views.py::application_withdraw, opportunity_apply`, `accounts/services.py::withdraw_application, apply_to_opportunity`, `accounts/models.py::Application`. **Frontend:** `templates/my_applications.html`, `templates/opportunity.html`. **Tests:** `tests/test_sprint3_lifecycle.py::test_withdraw_reapply_decisions_and_notification_ownership`; `tests/test_sprint3_integration.py::test_student_faculty_lifecycle_and_notifications_end_to_end`. **Status:** Implemented; manually verify controls and closed reapplication. Human acceptance is not recorded.

### US19: Faculty decisions — 3 points

**Story:** As a faculty owner, I want to shortlist or reject applicants, so that I can communicate selection decisions.

**Criteria:** Owners can change eligible applied, shortlisted or rejected applications to shortlisted or rejected. Withdrawn applications and foreign faculty decisions are denied. Changed decisions create notifications.

- **Positive:** Given an eligible application, when its owner chooses shortlist or reject, then status and change time update and a notification is created.
- **Negative:** Given a withdrawn application or foreign faculty member, when a decision is attempted, then the change is rejected.

**Implementation:** `accounts/views.py::application_decision`, `accounts/services.py::decide_application`, `accounts/models.py::Application, Notification`. **Frontend:** `templates/opportunity_applicants.html`. **Tests:** `tests/test_sprint3_lifecycle.py::test_withdraw_reapply_decisions_and_notification_ownership`; `tests/test_sprint3_integration.py::test_student_faculty_lifecycle_and_notifications_end_to_end`. **Status:** Implemented; manually verify decision confirmation and feedback. Human acceptance is not recorded.

### US20: Application status tracking — 2 points

**Story:** As a student, I want to see my application statuses and update times, so that I can track progress.

**Criteria:** Students see their own status, applied date and change date. Removed opportunities remain visible as history without opportunity links or actions; status filters use stored status values.

- **Positive:** Given a changed application, when its owner views My applications, then its current status and update date appear.
- **Negative:** Given an administrator-removed opportunity, when the student views history, then the record remains without opportunity actions.

**Implementation:** `accounts/views.py::my_applications`, `accounts/models.py::Application`. **Frontend:** `templates/my_applications.html`. **Tests:** `tests/test_sprint3_lifecycle.py::test_removed_and_hard_delete_preserve_application`; `tests/test_sprint3_moderation.py::test_moderation_removal_reports_and_historical_visibility`. **Status:** Implemented; manually verify status filters and date presentation. Human acceptance is not recorded.

### US21: Personalised recommendations — 5 points

**Story:** As a student, I want recommendations based on my skills, so that I can discover relevant opportunities.

**Criteria:** Recommendations include visible open opportunities with positive scored matches, excluding active applications. They sort by descending score, deadline, title and ID. Withdrawn applications can become eligible again. The dashboard requests three and the recommendations page ten.

- **Positive:** Given eligible positive matches, when recommendations are calculated, then results appear in the documented order.
- **Negative:** Given a removed, unscored, zero-scored or actively applied opportunity, when recommendations run, then it is excluded.

**Implementation:** `accounts/services.py::recommend_opportunities`, `accounts/views.py::recommendations, dashboard`, `accounts/matching.py::match_student`. **Frontend:** `templates/recommendations.html`, `templates/dashboard.html`, `templates/partials/opportunity_card.html`. **Tests:** `tests/test_sprint3_progress.py::test_recommendations_order_exclusions_and_improvements`. **Status:** Implemented; manually verify zero-score, unscored and empty states and dashboard limit. Human acceptance is not recorded.

### US22: Skill improvement suggestions — 3 points

**Story:** As a student, I want to see skills that could improve my matches, so that I can prioritise learning.

**Criteria:** Only missing or improvable skills are suggested. Potential gains use exact fractional score points aggregated across open opportunities and are ordered deterministically; the interface exposes target level and affected count.

- **Positive:** Given a missing or under-level requirement, when suggestions are calculated, then potential gains and target levels are provided.
- **Negative:** Given a fully met requirement, when suggestions are calculated, then it adds no improvement suggestion.

**Implementation:** `matching/advanced.py::suggest_improvements, _accumulate_improvement`, `accounts/services.py::student_improvements`, `accounts/views.py::improvements`. **Frontend:** `templates/improvements.html`. **Tests:** `tests/test_sprint3_matching.py::test_improvements_rank_total_gain_across_opportunities`, `test_improvement_ties_are_deterministic`, `test_fully_matched_skills_are_not_suggested`; `tests/test_sprint3_progress.py::test_recommendations_order_exclusions_and_improvements`. **Status:** Implemented; manually check links and explanation of points. Human acceptance is not recorded.

### US23: Decision notifications — 3 points

**Story:** As a student, I want to receive and manage decision notifications, so that I know when my application status changes.

**Criteria:** A changed faculty decision creates a notification transactionally for the applicant. Students view their own paginated inbox and mark individual or all own notifications read by POST; a foreign notification cannot be marked.

- **Positive:** Given a changed eligible decision, when the transaction completes, then the applicant has a notification.
- **Negative:** Given another student's notification or an unchanged decision, when the action is processed, then the foreign item is inaccessible or no duplicate decision notification is created.

**Implementation:** `accounts/services.py::decide_application`, `accounts/views.py::notification_inbox, notification_read, notification_read_all`, `accounts/models.py::Notification`. **Frontend:** `templates/notifications.html`, `templates/base.html`. **Tests:** `tests/test_sprint3_lifecycle.py::test_withdraw_reapply_decisions_and_notification_ownership`; `tests/test_sprint3_integration.py::test_student_faculty_lifecycle_and_notifications_end_to_end`. **Status:** Implemented; manually verify pagination, read-all and indicator presentation. Human acceptance is not recorded.

### US24: Team skill-gap analysis — 5 points

**Story:** As a faculty opportunity owner, I want to analyse selected applicants as a team, so that I can identify uncovered skills.

**Criteria:** Owners of visible project or research opportunities analyse non-withdrawn applicants. Shortlisted applicants are selected by default; explicit selections must be eligible student IDs. Coverage uses each requirement's best member level and reports covered, partial or gap states.

- **Positive:** Given eligible selected applicants, when the owner analyses a project or research team, then coverage uses the best level for each skill.
- **Negative:** Given an internship, foreign opportunity or tampered/ineligible member, when analysis is requested, then the request is denied or rejected.

**Implementation:** `accounts/views.py::team_gap`, `matching/advanced.py::analyze_team_gap, TeamMember, TeamGap`. **Frontend:** `templates/team_gap.html`, `templates/opportunity_applicants.html`. **Tests:** `tests/test_sprint3_matching.py::test_team_coverage_uses_best_member_for_each_skill`, `test_team_empty_and_no_requirements`; `tests/test_sprint3_lifecycle.py::test_team_gap_rejects_ineligible_ids_and_internships`. **Status:** Implemented; manually verify selection and empty states. Human acceptance is not recorded.

### US25: Administrator reports — 3 points

**Story:** As an administrator, I want aggregate platform reports, so that I can understand activity.

**Criteria:** Only administrators can access counts by user role and active status, visible opportunity status/type, removed opportunities, application status and active skills, and skill demand on visible opportunities.

- **Positive:** Given stored records, when an administrator opens reports, then aggregates reflect the records and visibility rules.
- **Negative:** Given a student or a removed opportunity, when reports or demand are requested, then access is denied or removed requirements are excluded from demand.

**Implementation:** `accounts/views.py::admin_reports`, `accounts/models.py::User, Opportunity, Application, Skill`. **Frontend:** `templates/admin_reports.html`, `static/js/report-chart.js`. **Tests:** `tests/test_sprint3_moderation.py::test_admin_user_moderation_and_inactive_sessions`, `test_moderation_removal_reports_and_historical_visibility`. **Status:** Implemented; manually reconcile all report categories and chart values. Human acceptance is not recorded.

### US26: Administrator moderation — 2 points

**Story:** As an administrator, I want to deactivate users and remove or restore opportunities, so that I can moderate the platform while retaining history.

**Criteria:** A superuser can deactivate or reactivate non-staff, non-superuser accounts and soft-remove or restore opportunities. Self, staff and superuser deactivation are denied. Removed opportunities are excluded from normal workflows while application history remains.

- **Positive:** Given a non-admin user or opportunity, when the administrator submits a valid moderation action, then access or visibility changes and history remains.
- **Negative:** Given a non-admin actor, protected account or invalid action, when moderation is attempted, then it is denied or rejected.

**Implementation:** `accounts/views.py::moderation, moderate_user, moderate_opportunity`, `accounts/services.py::set_user_active, set_opportunity_removed`. **Frontend:** `templates/moderation.html`. **Tests:** `tests/test_sprint3_moderation.py::test_admin_user_moderation_and_inactive_sessions`, `test_moderation_removal_reports_and_historical_visibility`. **Status:** Implemented; manually verify confirmations and invalid action feedback. Human acceptance is not recorded.

### US27: Automatic deadline closure — 2 points

**Story:** As a faculty member, I want expired opportunities closed, so that late applications are prevented.

**Criteria:** Visible published opportunities close when deadline is before the local date; deadline day remains open. Closure is idempotent and runs on opportunity-list and faculty-dashboard visits or via a management command; no continuously running scheduler is provided.

- **Positive:** Given a visible published opportunity with a past deadline, when closure runs, then its status becomes closed.
- **Negative:** Given a deadline today, removed opportunity or a repeat run, when closure runs, then due-today and removed records are unchanged and the repeat makes no further change.

**Implementation:** `accounts/services.py::close_expired_opportunities`, `accounts/views.py::dashboard, opportunity_list`, `accounts/management/commands/close_expired_opportunities.py::Command`. **Frontend:** `templates/opportunity_list.html`, `templates/dashboard.html`. **Tests:** `tests/test_sprint3_progress.py::test_close_expired_is_idempotent_and_preserves_deadline_day`; `tests/test_matching_workflows.py::test_open_boundary_uses_local_date_for_property_and_queryset`. **Status:** Implemented; manually verify deployment scheduling if closure must happen without visits. Human acceptance is not recorded.

### US28: Profile completeness — 2 points

**Story:** As a student, I want to see profile completeness, so that I can identify missing information.

**Criteria:** Five checks contribute 20 points each: branch and academic year together, interests, at least three skills, at least one project, and at least one certification. The dashboard and profile surfaces display the checklist and links for incomplete checks.

- **Positive:** Given all five checks are satisfied, when completeness is displayed, then the result is 100% and the checklist is complete.
- **Negative:** Given missing checks, when completeness is calculated, then each missing check contributes zero.

**Implementation:** `accounts/services.py::profile_completeness`, `accounts/views.py::student_completeness, dashboard, profile_overview, profile_edit`. **Frontend:** `templates/partials/completeness.html`, `templates/dashboard.html`, `templates/profile_overview.html`, `templates/form.html`. **Tests:** `tests/test_sprint3_progress.py::test_completeness_checklist`. **Status:** Implemented; manually verify checklist links, partial states and profile surfaces. Human acceptance is not recorded.

## Definition of Done

- Acceptance criteria are demonstrated with valid inputs, relevant invalid and boundary cases, role and object ownership checks, and preserved data.
- Changes are reviewed; relevant automated tests, Django system and migration checks, and Ruff checks pass.
- User-facing workflows are checked for usability and accessibility, including appropriate desktop and mobile layouts.
- Evidence references actual tests, commits and checks; human acceptance, production readiness and collaboration records are not inferred.
- Integration into the stable branch follows the project's review and approval rules.

## Acceptance verification summary

The matrix identifies implementation and existing automated evidence, not blanket proof of all criteria. Manual checks in each story remain open until a reviewer records actual outcomes. Run the complete suite with `python -m pytest -q` and record actual results. See [TDD.md](TDD.md) for the genuine RED–GREEN–REFACTOR evidence, which is unchanged.

On 26 November 2026, the documentation branch based on merged `main` commit `d43c9f1` passed **48 tests** locally (one Django deprecation warning). Ruff lint and formatting, Django system checks and the missing-migration check also passed. These results do not establish human acceptance or verify all manual scenarios.

### Requirements traceability matrix

| Story | Points | Implementation | Existing automated evidence |
| --- | ---: | --- | --- |
| [US1](#us1-student-and-faculty-registration--3-points) | 3 | [views](../accounts/views.py) | [workflows](../tests/test_workflows.py) |
| [US2](#us2-login-and-logout--3-points) | 3 | [forms](../accounts/forms.py) | [workflows](../tests/test_workflows.py) |
| [US3](#us3-student-profile--2-points) | 2 | [views](../accounts/views.py) | [workflows](../tests/test_workflows.py) |
| [US4](#us4-add-student-skills--3-points) | 3 | [models](../accounts/models.py) | [workflows](../tests/test_workflows.py) |
| [US5](#us5-edit-and-remove-student-skills--2-points) | 2 | [views](../accounts/views.py) | [workflows](../tests/test_workflows.py) |
| [US6](#us6-student-projects--2-points) | 2 | [models](../accounts/models.py) | [workflows](../tests/test_workflows.py) |
| [US7](#us7-student-certifications--2-points) | 2 | [models](../accounts/models.py) | [workflows](../tests/test_workflows.py) |
| [US8](#us8-faculty-opportunities--3-points) | 3 | [views](../accounts/views.py) | [workflows](../tests/test_workflows.py) |
| [US9](#us9-required-skills-levels-and-weights--5-points) | 5 | [models](../accounts/models.py) | [workflows](../tests/test_workflows.py) |
| [US10](#us10-administrator-skill-catalogue--2-points) | 2 | [catalogue service](../skills/services.py) | [skill tests](../tests/test_skill_names.py) |
| [US11](#us11-browse-and-search-opportunities--3-points) | 3 | [views](../accounts/views.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US12](#us12-opportunity-filters--3-points) | 3 | [views](../accounts/views.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US13](#us13-weighted-skill-matching--8-points) | 8 | [engine](../matching/__init__.py) | [engine tests](../tests/test_matching_engine.py) |
| [US14](#us14-skill-fit-explanations--5-points) | 5 | [views](../accounts/views.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US15](#us15-apply-to-opportunities--3-points) | 3 | [services](../accounts/services.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US16](#us16-faculty-applicant-view--2-points) | 2 | [views](../accounts/views.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US17](#us17-rank-applicants--5-points) | 5 | [engine](../matching/__init__.py) | [matching workflows](../tests/test_matching_workflows.py) |
| [US18](#us18-withdraw-and-reapply--2-points) | 2 | [services](../accounts/services.py) | [lifecycle tests](../tests/test_sprint3_lifecycle.py) |
| [US19](#us19-faculty-decisions--3-points) | 3 | [services](../accounts/services.py) | [lifecycle tests](../tests/test_sprint3_lifecycle.py) |
| [US20](#us20-application-status-tracking--2-points) | 2 | [views](../accounts/views.py) | [lifecycle tests](../tests/test_sprint3_lifecycle.py) |
| [US21](#us21-personalised-recommendations--5-points) | 5 | [services](../accounts/services.py) | [progress tests](../tests/test_sprint3_progress.py) |
| [US22](#us22-skill-improvement-suggestions--3-points) | 3 | [advanced matching](../matching/advanced.py) | [matching tests](../tests/test_sprint3_matching.py) |
| [US23](#us23-decision-notifications--3-points) | 3 | [services](../accounts/services.py) | [lifecycle tests](../tests/test_sprint3_lifecycle.py) |
| [US24](#us24-team-skill-gap-analysis--5-points) | 5 | [advanced matching](../matching/advanced.py) | [matching tests](../tests/test_sprint3_matching.py) |
| [US25](#us25-administrator-reports--3-points) | 3 | [views](../accounts/views.py) | [moderation tests](../tests/test_sprint3_moderation.py) |
| [US26](#us26-administrator-moderation--2-points) | 2 | [services](../accounts/services.py) | [moderation tests](../tests/test_sprint3_moderation.py) |
| [US27](#us27-automatic-deadline-closure--2-points) | 2 | [services](../accounts/services.py) | [progress tests](../tests/test_sprint3_progress.py) |
| [US28](#us28-profile-completeness--2-points) | 2 | [services](../accounts/services.py) | [progress tests](../tests/test_sprint3_progress.py) |

**Total: 88 initial story points.** Exact functions, templates, scenarios and outstanding manual checks appear in the individual story sections.
