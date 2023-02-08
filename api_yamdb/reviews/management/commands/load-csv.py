from csv import DictReader

from django.core.management import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)


class Command(BaseCommand):
    help = 'Загружает данные из CSV файлов в папке static/data'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        for row in DictReader(
            open('./static/data/' + csv_file + '.csv', encoding='utf-8')
        ):
            if csv_file == 'category':
                category = Category(
                    id=row['id'], name=row['name'], slug=row['slug']
                )
                category.save()
            elif csv_file == 'comments':
                comment = Comment(
                    id=row['id'],
                    review=get_object_or_404(Review, pk=row['review_id']),
                    text=row['text'],
                    author=get_object_or_404(User, pk=row['author']),
                    pub_date=row['pub_date'],
                )
                comment.save()
            elif csv_file == 'genre_title':
                genre_title = GenreTitle(
                    title=get_object_or_404(Title, pk=row['title_id']),
                    genre=get_object_or_404(Genre, pk=row['genre_id']),
                )
                genre_title.save()
            elif csv_file == 'genre':
                genre = Genre(id=row['id'], name=row['name'], slug=row['slug'])
                genre.save()
            elif csv_file == 'review':
                review = Review(
                    id=row['id'],
                    title=get_object_or_404(Title, pk=row['title_id']),
                    text=row['text'],
                    author=get_object_or_404(User, pk=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date'],
                )
                review.save()
            elif csv_file == 'titles':
                title = Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=get_object_or_404(Category, pk=row['category']),
                )
                title.save()
            elif csv_file == 'users':
                user = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                )
                user.save()
        print('Файл загружен.')
