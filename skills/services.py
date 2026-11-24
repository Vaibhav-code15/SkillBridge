def skill_name_exists(name, existing_names):
    """Return whether a catalogue already contains a skill name."""
    return any(name.lower() == existing.lower() for existing in existing_names)
