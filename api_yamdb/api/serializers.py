from datetime import datetime
from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator

from api_yamdb.settings import MAX_SCORE, MIN_SCORE
from reviews.models import Category, Comment, Genre, Title, Review


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].year > datetime.today().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = '__all__'


class CurrentTitle:
    requires_context = True

    def __call__(self, serializer_field):
        return (
            serializer_field.context.get('request')
            .parser_context.get('kwargs')
            .get('title_id')
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentTitle(),
    )
    score = serializers.IntegerField(
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
        model = Review
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
            )
        ]
