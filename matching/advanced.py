"""Pure skill-improvement and team-gap analysis interfaces."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from matching import RequiredSkillInput


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


def suggest_improvements(
    student_levels: Mapping[int, int],
    opportunities: Sequence[Sequence[RequiredSkillInput]],
) -> tuple[Improvement, ...]:
    raise NotImplementedError("Skill improvement suggestions are not implemented yet")


def analyze_team_gap(
    requirements: Sequence[RequiredSkillInput], members: Sequence[TeamMember]
) -> TeamGap:
    raise NotImplementedError("Team gap analysis is not implemented yet")
