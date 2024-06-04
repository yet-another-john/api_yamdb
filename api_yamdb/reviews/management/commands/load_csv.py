import csv

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

from api_yamdb.settings import CSV_FILES_DIR

models_files: dict = {
    Genre: 'genre.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    User: 'users.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    """Класс загрузки тестовых данных базы."""
    help: str = 'load data from csv'

    for model in models_files.keys():
        model.objects.all().delete()

    def handle(self, *args, **options):

        for model, csv_file in models_files.items():
            with open(CSV_FILES_DIR + '\\' + csv_file, 'r',
                      encoding='utf-8') as file:
                csv_reader = csv.DictReader(file, delimiter=',')
                records = [model(**row) for row in csv_reader]
                model.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(
                f'Приняты данные {model.__name__}'))
