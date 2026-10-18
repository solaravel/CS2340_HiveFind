from django.contrib import admin

from .models import Job, Report


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'city', 'state', 'is_remote', 'created_at')
    list_filter = ('is_remote', 'state')
    search_fields = ('title', 'company', 'city')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reason", "status", "reporter", "reported_user", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("details", "reporter__username", "reported_user__username")
    readonly_fields = ("reporter", "reported_user", "reported_posting", "reason", "details", "created_at")
    actions = ["resolve_and_hide", "mark_reviewing", "mark_dismissed"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ("created_at",)

    def save_model(self, request, obj, form, change):
        if not obj.reporter:
            obj.reporter = request.user
        super().save_model(request, obj, form, change)


    @admin.action(description="Hide reported job and mark resolved")
    def resolve_and_hide(self, request, queryset):
        for report in queryset:
            if report.reported_posting:
                report.reported_posting.is_active = False
                report.reported_posting.save()
            report.status = Report.ReportStatus.RESOLVED
            report.save()

    @admin.action(description="Mark as Under Review")
    def mark_reviewing(self, request, queryset):
        for report in queryset:
            report.status = Report.ReportStatus.REVIEWING
            report.save()

    @admin.action(description="Mark as Dismissed")
    def mark_dismissed(self, request, queryset):
        for report in queryset:
            report.status = Report.ReportStatus.DISMISSED
            report.save()