from django.contrib import admin
from django.contrib.admin import ModelAdmin

from reviews.models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('id', 'review', 'text', 'author', 'pub_date')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(ModelAdmin):
    list_display = ('id', 'name', 'year', 'description', 'category',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('id', 'title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('text',)
    list_filter = ('text',)
    empty_value_display = '-пусто-'
