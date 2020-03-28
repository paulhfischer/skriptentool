from django.contrib import admin

from core.models import DepositNote


@admin.register(DepositNote)
class DepositNoteAdmin(admin.ModelAdmin):
    fields = ["number", "price", ("sold_time", "sold_by"), ("refunded_time", "refunded_by"), "refundable"]
    readonly_fields = ["number", "price", "sold_time", "sold_by", "refunded_time", "refunded_by"]

    list_display = ["number", "price", "sold_time", "refunded_time", "refundable"]
    list_display_links = ["number"]
    list_editable = ["refundable"]
    list_filter = ["refundable"]

    search_fields = ["number"]

    ordering = ["-number"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent
