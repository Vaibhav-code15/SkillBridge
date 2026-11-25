"""ORM adapters between account models and the pure matching engine."""

from accounts.models import Opportunity, User
from matching import MatchResult, RequiredSkillInput, calculate_match


def requirements_for(opportunity: Opportunity) -> tuple[RequiredSkillInput, ...]:
    return tuple(
        RequiredSkillInput(
            skill_id=item.skill_id,
            name=item.skill.name,
            minimum=item.minimum_proficiency,
            weight=item.weight,
        )
        for item in opportunity.requirements.all()
    )


def skill_levels_for(student: User) -> dict[int, int]:
    return {item.skill_id: item.proficiency for item in student.student_skills.all()}


def match_student(
    requirements: tuple[RequiredSkillInput, ...],
    student: User,
    skill_levels: dict[int, int] | None = None,
) -> MatchResult:
    levels = skill_levels_for(student) if skill_levels is None else skill_levels
    return calculate_match(requirements, levels)
