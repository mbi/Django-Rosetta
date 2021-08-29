import django

VERSION = (0, 9, 8)

if django.VERSION[:3] <= (3, 2, 0):
    default_app_config = "rosetta.apps.RosettaAppConfig"


def get_version(limit=3):
    """Return the version as a human-format string."""
    return '.'.join([str(i) for i in VERSION[:limit]])
