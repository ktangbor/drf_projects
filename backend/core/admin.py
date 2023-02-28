from django.contrib import admin
from .models import Profile, ProgrammingSkill


@admin.register(Profile)
class ItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ProgrammingSkill)
class ItemAdmin(admin.ModelAdmin):
    pass
