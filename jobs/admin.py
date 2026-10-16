from django.contrib import admin

from .models import Job, Report


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'city', 'state', 'is_remote', 'created_at')
    list_filter = ('is_remote', 'state')
    search_fields = ('title', 'company', 'city')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reason", "status", "reporter", "target_link", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("details", "reporter__username", "reported_user__username", "reported_posting__title")
    # stopped here
    @admin.display(description="Reported")
    def target_link(self, obj):
        pass