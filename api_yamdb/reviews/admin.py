from django.contrib import admin

from .models import (
    Category,
    Comment,
    Genre,
    Title,
    Review
)

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
class TitleAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'review', 'text')


@admin.register(Review)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_filter = ('pub_date', 'author', 'title', 'score', 'text')
