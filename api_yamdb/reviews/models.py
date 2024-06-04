from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from api_yamdb.settings import LENGTH_MAX, LENGTH_TEXT

from .validators import my_year_validator

User = get_user_model()

MIN_SCORE = 1
MAX_SCORE = 10


class CategoryGenreAbstract(models.Model):
    name = models.CharField(max_length=LENGTH_MAX, verbose_name="Название")
    slug = models.SlugField(
        max_length=50,
        verbose_name="slug",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Недопустимый символ в слаге ",
            )
        ],
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name[:LENGTH_TEXT]


class Category(CategoryGenreAbstract):
    """Класс категорий."""

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)


class Genre(CategoryGenreAbstract):
    """Класс жанров."""

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("name",)


class Title(models.Model):
    """Класс произведений."""

    name = models.CharField(
        max_length=LENGTH_MAX,
        verbose_name="Название",
    )
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска",
        validators=[my_year_validator],
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    genre = models.ManyToManyField(
        Genre, related_name="titles", verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="категория",
        null=True,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self) -> str:
        return self.name[:LENGTH_TEXT]


class ReviewCommentAbstract(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор отзыва",
        on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.text[:LENGTH_TEXT]


class Review(ReviewCommentAbstract):
    """Класс отзывы."""
    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name="titles")
    score = models.PositiveIntegerField(
        verbose_name="Оценка",
        validators=[
            MinValueValidator(
                MIN_SCORE, message="Оценка не может быть меньше 1"),
            MaxValueValidator(
                MAX_SCORE, message="Оценка не может быть больше 10"),
        ],)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [models.UniqueConstraint(
            fields=("author", "title"), name="Unique review")]


class Comment(ReviewCommentAbstract):
    """Класс комментарии."""

    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name="reviews")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
