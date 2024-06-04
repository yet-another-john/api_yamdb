from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    username = models.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='В имени пользователя только буквы, цифры и @/./+/-/_'
        )],
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            (USER, "user"),
            (MODERATOR, "moderator"),
            (ADMIN, "admin"),
        ],
        default='user',
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        blank=True,
        max_length=20,
        verbose_name='Код подтверждения'
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_user(self):
        return self.role == User.USER
