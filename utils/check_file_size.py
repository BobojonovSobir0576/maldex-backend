from rest_framework.exceptions import ValidationError


def validate_file_size(value):
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError((f'File size must be no more than 2 mb.'), params={'max_size': max_size},)
