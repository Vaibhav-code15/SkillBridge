from fractions import Fraction

import pytest

from matching import RequiredSkillInput, calculate_match


def requirement(skill_id: int, minimum: int = 2, weight: int = 1) -> RequiredSkillInput:
    return RequiredSkillInput(skill_id, f"Skill {skill_id}", minimum, weight)


def test_full_match_scores_100():
    result = calculate_match([requirement(1, minimum=3)], {1: 4})

    assert result.score == 100
    assert result.skills[0].status == "matched"


def test_no_matching_skills_scores_zero_and_classifies_missing():
    result = calculate_match([requirement(1), requirement(2)], {})

    assert result.score == 0
    assert {skill.status for skill in result.skills} == {"missing"}
    assert all(skill.credit == 0 for skill in result.skills)


def test_under_level_skill_receives_proportional_credit():
    result = calculate_match([requirement(1, minimum=4)], {1: 2})

    assert result.score == 50
    assert result.skills[0].status == "improvable"
    assert result.skills[0].credit == Fraction(1, 2)
    assert result.skills[0].points == Fraction(50, 1)


def test_weights_change_the_overall_result():
    result = calculate_match(
        [requirement(1, minimum=1, weight=3), requirement(2, minimum=1, weight=1)],
        {1: 1},
    )

    assert result.score == 75
    assert [skill.points for skill in result.skills] == [Fraction(75), Fraction(0)]


def test_groups_matched_improvable_and_missing_skills():
    result = calculate_match(
        [requirement(1, minimum=2), requirement(2, minimum=4), requirement(3, minimum=1)],
        {1: 3, 2: 1},
    )

    assert [skill.status for skill in result.skills] == ["matched", "improvable", "missing"]


def test_empty_requirements_are_unscored_and_inputs_are_validated():
    assert calculate_match([], {}).score is None

    with pytest.raises(ValueError):
        calculate_match([requirement(1), requirement(1)], {1: 2})
    with pytest.raises(ValueError):
        calculate_match([requirement(1, minimum=5)], {1: 2})
    with pytest.raises(ValueError):
        calculate_match([requirement(1, weight=0)], {1: 2})
    with pytest.raises(ValueError):
        calculate_match([requirement(1)], {1: 5})


def test_half_up_rounds_62_point_5_to_63():
    result = calculate_match([requirement(1, minimum=1), requirement(2, minimum=4)], {1: 1, 2: 1})

    assert result.score == 63
