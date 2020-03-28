from django.contrib import admin

from core.models import PrintingQuota


@admin.register(PrintingQuota)
class PrintingQuotaAdmin(admin.ModelAdmin):
    fields = ["ean", "pages", "price", "active"]
    readonly_fields = []

    list_display = ["ean", "pages", "price", "active"]
    list_display_links = ["ean"]
    list_editable = ["active"]
    list_filter = ["active"]

    search_fields = ["ean"]

    ordering = ["-ean"]

    def has_add_permission(self, request):
        return request.user.is_referent

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent

    def has_delete_permission(self, request, obj=None):
        return request.user.is_referent

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent
