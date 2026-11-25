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


def calculate_match(
    requirements: Sequence[RequiredSkillInput], student_levels: Mapping[int, int]
) -> MatchResult:
    """Return weighted fit results for one student's skills and one opportunity."""
    raise NotImplementedError
