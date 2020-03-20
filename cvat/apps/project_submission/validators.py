import os
from django.core.exceptions import ValidationError


def validate_extension_is_json(filename: str):
    expected_extension = ".json"
    extension = os.path.splitext(filename)[1]
    if not extension.lower() == expected_extension.lower():
        raise ValidationError('Expected extension' + expected_extension + 'but got' + extension)
