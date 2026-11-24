from skills.services import skill_name_exists


def test_duplicate_skill_name_is_case_insensitive():
    assert skill_name_exists("python", ["Python"])


def test_distinct_skill_name_is_available():
    assert not skill_name_exists("Django", ["Python"])
