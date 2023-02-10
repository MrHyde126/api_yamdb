from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import serializers

from api_yamdb.settings import ADMIN, DEFAULT_FROM_EMAIL, MODERATOR, USER
from reviews.models import User


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
    elif data['username'].lower() == 'me':
        raise serializers.ValidationError(
            'Пользователя с именем "me" нельзя создать'
        )


def check_email(data):
    if User.objects.filter(email=data['email'].lower()):
        raise serializers.ValidationError(
            'Пользователь с таким email уже зарегистрирован'
        )


def check_role(data):
    if data['role'] not in (USER, MODERATOR, ADMIN):
        raise serializers.ValidationError('Выбрана несуществующая роль')
