from django.core.exceptions import ValidationError
from django.utils import timezone


def my_year_validator(value):
    if value < 0 or value > timezone.now().year:
        raise ValidationError(
            ('%(value)s некорректное значение'),
            params={'value': value},
        )
