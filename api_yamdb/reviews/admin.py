from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('category', 'genre', 'name', 'year')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'review')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'title', 'score')
