"""
Settings file for use in testing
"""
import os
from .settings import *

COUNT_API_CALLS = True
MEDIA_ROOT = os.path.join(BASE_DIR, 'api/tests/media/')
SEND_EMAIL = False
