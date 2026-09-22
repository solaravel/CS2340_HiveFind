from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'city', 'state', 'is_remote', 'created_at')
    list_filter = ('is_remote', 'state')
    search_fields = ('title', 'company', 'city')
