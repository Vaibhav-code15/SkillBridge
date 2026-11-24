def skill_name_exists(name, existing_names):
    """Return whether a catalogue already contains a skill name."""
    normalized_name = name.lower()
    return any(existing.lower() == normalized_name for existing in existing_names)
