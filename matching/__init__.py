"""Pure Python skill matching engine."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class RequiredSkillInput:
    skill_id: int
    name: str
    minimum: int
    weight: int


@dataclass(frozen=True, slots=True)
class SkillMatch:
    skill_id: int
    name: str
    status: str
    student_level: int
    minimum: int
    weight: int
    credit: Fraction
    points: Fraction


@dataclass(frozen=True, slots=True)
class MatchResult:
    score: int | None
    skills: tuple[SkillMatch, ...]


def _classify_skill(student_level: int, minimum: int) -> tuple[str, Fraction]:
    if student_level == 0:
        return "missing", Fraction(0)
    if student_level < minimum:
        return "improvable", Fraction(student_level, minimum)
    return "matched", Fraction(1)


def _round_half_up(value: Fraction) -> int:
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def calculate_match(
    requirements: Sequence[RequiredSkillInput], student_levels: Mapping[int, int]
) -> MatchResult:
    """Return weighted fit results for one student's skills and one opportunity."""
    seen: set[int] = set()
    for requirement in requirements:
        if requirement.skill_id in seen:
            raise ValueError("Requirement skill ids must be unique.")
        seen.add(requirement.skill_id)
        if requirement.minimum not in range(1, 5):
            raise ValueError("Minimum proficiency must be between 1 and 4.")
        if requirement.weight <= 0:
            raise ValueError("Requirement weights must be positive.")

    if any(level not in range(5) for level in student_levels.values()):
        raise ValueError("Student proficiency levels must be between 0 and 4.")

    total_weight = sum(requirement.weight for requirement in requirements)
    if not requirements:
        return MatchResult(score=None, skills=())

    results = []
    weighted_credit = Fraction(0)
    for requirement in requirements:
        student_level = student_levels.get(requirement.skill_id, 0)
        status, credit = _classify_skill(student_level, requirement.minimum)

        weighted_credit += requirement.weight * credit
        results.append(
            SkillMatch(
                skill_id=requirement.skill_id,
                name=requirement.name,
                status=status,
                student_level=student_level,
                minimum=requirement.minimum,
                weight=requirement.weight,
                credit=credit,
                points=Fraction(100 * requirement.weight, total_weight) * credit,
            )
        )

    exact_score = 100 * weighted_credit / total_weight
    score = _round_half_up(exact_score)
    return MatchResult(score=score, skills=tuple(results))
