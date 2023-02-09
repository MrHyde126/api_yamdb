from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api_yamdb.settings import DEFAULT_FROM_EMAIL, MAX_SCORE, MIN_SCORE
from reviews.models import Category, Comment, Genre, Review, Title, User


def send_mail_token(user):
    token = default_token_generator.make_token(user)
    send_mail(
        subject='Код для входа на сайт',
        message=f'Для входа на сайт - {token}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=(user.email,),
    )


def check_user(data):
    if User.objects.filter(username=data['username']):
        raise serializers.ValidationError(
            'Пользователь с таким именем уже существует'
        )
    elif data['username'] == 'me':
        raise serializers.ValidationError(
            'Пользователя с именем "me" нельзя создать'
        )


def check_email(data):
    if User.objects.filter(email=data['email']):
        raise serializers.ValidationError(
            'Пользователь с таким email уже зарегистрирован'
        )


def check_role(data):
    if data['role'] not in ('user', 'moderator', 'admin'):
        raise serializers.ValidationError('Выбрана несуществующая роль')


class SendCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Неверно заполнено имя пользователя',
            ),
        ],
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        user = User.objects.filter(
            username=data['username'], email=data['email']
        )
        if user:
            send_mail_token(user)
            raise serializers.ValidationError(
                'Для входа на сайт введите код отправленный на вашу почту'
            )
        check_user(data)
        check_email(data)
        return data

    def create(self, data):
        user = User.objects.create(**data)
        send_mail_token(user)
        return user


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if username is None:
            raise serializers.ValidationError(
                f'Пользователь {username} отсутствует'
            )
        if confirmation_code is None:
            raise serializers.ValidationError('Отсутствует код подтверждения')
        return data


class UserMeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Неверно заполнено имя пользователя',
            ),
        ],
        required=True,
        max_length=150,
    )
    last_name = serializers.CharField(required=False, max_length=150)
    first_name = serializers.CharField(required=False, max_length=150)
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=True, max_length=254)
    role = serializers.CharField(required=False, default='user')

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        lookup_field = 'username'

    def validate(self, attrs):
        if 'username' in attrs:
            check_user(attrs)
        if 'email' in attrs:
            check_email(attrs)
        if 'role' in attrs:
            check_role(attrs)
        return attrs


class UserEditMeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Неверно заполнено имя пользователя',
            ),
        ],
        required=False,
        max_length=150,
    )
    last_name = serializers.CharField(required=False, max_length=150)
    first_name = serializers.CharField(required=False, max_length=150)
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, max_length=254)
    role = serializers.CharField(
        required=False, default='user', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate(self, attrs):
        if 'username' in attrs:
            check_user(attrs)
        if 'email' in attrs:
            check_email(attrs)
        return attrs


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostPatchSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        if value > datetime.today().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


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
                message=f'Оценка не может быть меньше {MIN_SCORE}',
            ),
            MaxValueValidator(
                limit_value=MAX_SCORE,
                message=f'Оценка не может быть больше {MAX_SCORE}',
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
