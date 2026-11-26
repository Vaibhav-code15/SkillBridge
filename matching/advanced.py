"""Pure skill-improvement and team-gap analysis interfaces."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from matching import RequiredSkillInput, SkillMatch, calculate_match


@dataclass(frozen=True, slots=True)
class Improvement:
    skill_id: int
    name: str
    current_level: int
    target_level: int
    gain: Fraction
    opportunities_affected: int


@dataclass(frozen=True, slots=True)
class TeamMember:
    member_id: int
    name: str
    levels: Mapping[int, int]


@dataclass(frozen=True, slots=True)
class TeamSkillGap:
    skill_id: int
    name: str
    status: str
    best_level: int
    minimum: int
    weight: int
    covering_members: tuple[TeamMember, ...]


@dataclass(frozen=True, slots=True)
class TeamGap:
    score: int | None
    skills: tuple[TeamSkillGap, ...]
    empty_team: bool


def _accumulate_improvement(
    skill: SkillMatch, total_weight: int, previous: Improvement | None
) -> Improvement:
    gain = Fraction(100 * skill.weight, total_weight) * (1 - skill.credit)
    return Improvement(
        skill_id=skill.skill_id,
        name=skill.name,
        current_level=skill.student_level,
        target_level=max(skill.minimum, previous.target_level if previous else 0),
        gain=gain + (previous.gain if previous else 0),
        opportunities_affected=1 + (previous.opportunities_affected if previous else 0),
    )


def _team_skill_gap(skill: SkillMatch, members: Sequence[TeamMember]) -> TeamSkillGap:
    statuses = {"matched": "covered", "improvable": "partially covered", "missing": "gap"}
    return TeamSkillGap(
        skill_id=skill.skill_id,
        name=skill.name,
        status=statuses[skill.status],
        best_level=skill.student_level,
        minimum=skill.minimum,
        weight=skill.weight,
        covering_members=tuple(
            member for member in members if member.levels.get(skill.skill_id, 0) >= skill.minimum
        ),
    )


def suggest_improvements(
    student_levels: Mapping[int, int],
    opportunities: Sequence[Sequence[RequiredSkillInput]],
) -> tuple[Improvement, ...]:
    totals: dict[int, Improvement] = {}
    for requirements in opportunities:
        result = calculate_match(requirements, student_levels)
        total_weight = sum(item.weight for item in requirements)
        for skill in result.skills:
            if skill.status == "matched":
                continue
            totals[skill.skill_id] = _accumulate_improvement(
                skill, total_weight, totals.get(skill.skill_id)
            )
    return tuple(
        sorted(
            totals.values(),
            key=lambda item: (
                -item.gain,
                -item.opportunities_affected,
                item.name.casefold(),
                item.skill_id,
            ),
        )
    )


def analyze_team_gap(
    requirements: Sequence[RequiredSkillInput], members: Sequence[TeamMember]
) -> TeamGap:
    levels = {
        item.skill_id: max((member.levels.get(item.skill_id, 0) for member in members), default=0)
        for item in requirements
    }
    result = calculate_match(requirements, levels)
    skills = tuple(_team_skill_gap(item, members) for item in result.skills)
    return TeamGap(score=result.score, skills=skills, empty_team=not members)
