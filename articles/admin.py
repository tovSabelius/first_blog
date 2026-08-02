from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'text', 'date_publish', 'photo', 'slug']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Category)
class CategAdmin(admin.ModelAdmin):
    list_display = ['cat_name', 'slug']
    prepopulated_fields = {'slug': ('cat_name',)}
