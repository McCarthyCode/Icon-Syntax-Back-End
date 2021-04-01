from django.core.exceptions import ValidationError
from typing import Any

class ConflictError(Exception):
    """
    Exception to be used with the HTTP 409 CONFLICT status code.
     Inherits from django.core.exceptions.ValidationError.
    """
    def __init__(self, detail: Any):
        self.detail = detail
