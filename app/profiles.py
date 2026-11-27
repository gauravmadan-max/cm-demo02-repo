"""Workspace profile import helpers."""

from typing import Any, Dict

import yaml


def parse_profile_config(raw_yaml: str) -> Dict[str, Any]:
    """Parse a user-supplied YAML workspace profile."""
    loaded = yaml.load(raw_yaml, Loader=yaml.Loader)
    if not isinstance(loaded, dict):
        raise ValueError("Profile configuration must be a YAML mapping")
    return loaded
