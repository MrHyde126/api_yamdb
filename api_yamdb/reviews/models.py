from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from api_yamdb.settings import MAX_SCORE, MIN_SCORE


User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание', blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        related_name='reviews',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Отзыв',
        blank=True,
        null=False,
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Рецензирующий',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                limit_value=MIN_SCORE,
                message=f'Оценка не может быть меньше {MIN_SCORE}'
            ),
            MaxValueValidator(
                limit_value=MAX_SCORE,
                message=f'Оценка не может быть больше {MAX_SCORE}'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Комментарии',
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации отзыва',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
