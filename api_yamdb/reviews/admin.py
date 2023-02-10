from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    list_filter = ('role',)
    list_per_page = 30


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 30


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 30


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('category', 'genre__name', 'year')
    list_per_page = 30


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('text', 'review__text')
    list_filter = ('pub_date', 'author')
    list_per_page = 30


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'score')
    list_per_page = 30
