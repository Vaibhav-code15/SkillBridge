"""Local runserver settings; deployment entrypoints use config.settings."""

import os

from .settings import *

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
