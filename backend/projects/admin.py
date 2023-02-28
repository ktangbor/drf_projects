from django.contrib import admin
from . import models


@admin.register(models.Project)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(models.Collaborator)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(models.Candidate)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id',)
