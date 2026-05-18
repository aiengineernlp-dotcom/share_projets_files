from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'director', 'release_date', 'rating', 'duration')
    list_filter = ('release_date', 'rating')
    search_fields = ('name', 'director', 'description')
    ordering = ('-release_date', 'name')
    date_hierarchy = 'release_date'
