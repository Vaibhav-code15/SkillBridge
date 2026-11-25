from fractions import Fraction

from matching import RequiredSkillInput
from matching.advanced import TeamMember, analyze_team_gap, suggest_improvements


def test_improvements_rank_total_gain_across_opportunities():
    python = RequiredSkillInput(1, "Python", 4, 3)
    sql = RequiredSkillInput(2, "SQL", 2, 1)
    results = suggest_improvements({1: 2}, [[python, sql], [python]])
    assert [item.skill_id for item in results] == [1, 2]
    assert results[0].gain == Fraction(175, 2)
    assert results[0].target_level == 4
    assert results[0].opportunities_affected == 2


def test_improvement_ties_are_deterministic():
    items = [
        RequiredSkillInput(4, "beta", 1, 1),
        RequiredSkillInput(2, "Alpha", 1, 1),
        RequiredSkillInput(1, "alpha", 1, 1),
    ]
    assert [item.skill_id for item in suggest_improvements({}, [items])] == [1, 2, 4]


def test_fully_matched_skills_are_not_suggested():
    assert suggest_improvements({1: 3}, [[RequiredSkillInput(1, "Python", 2, 1)]]) == ()


def test_team_coverage_uses_best_member_for_each_skill():
    reqs = [RequiredSkillInput(1, "Python", 4, 1), RequiredSkillInput(2, "SQL", 2, 1)]
    members = [TeamMember(1, "A", {1: 2, 2: 2}), TeamMember(2, "B", {1: 4})]
    result = analyze_team_gap(reqs, members)
    assert result.score == 100
    assert [item.best_level for item in result.skills] == [4, 2]
    assert [item.status for item in result.skills] == ["covered", "covered"]
    assert [member.name for member in result.skills[0].covering_members] == ["B"]


def test_team_missing_skill_is_a_gap():
    result = analyze_team_gap([RequiredSkillInput(1, "Python", 2, 1)], [TeamMember(1, "A", {})])
    assert result.score == 0
    assert result.skills[0].status == "gap"
    assert result.skills[0].covering_members == ()


def test_team_empty_and_no_requirements():
    result = analyze_team_gap([RequiredSkillInput(1, "Python", 2, 1)], [])
    assert result.empty_team and result.score == 0 and result.skills[0].status == "gap"
    assert analyze_team_gap([], []).score is None
