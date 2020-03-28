from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from core.models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    # set editability of payout- and valid-field depending on group
    def get_changelist(self, request, **kwargs):
        fields = []
        if request.user.is_financier:
            fields += ["payout"]
        if request.user.is_referent:
            fields += ["valid"]
        self.list_editable = fields
        return super(ShiftAdmin, self).get_changelist(request, **kwargs)

    # set editability of payout- and valid-field depending on group
    def get_form(self, request, obj=None, **kwargs):
        fields = ["time_start", "time_end"]
        if not request.user.is_financier:
            fields += ["payout"]
        if not request.user.is_referent:
            fields += ["valid"]
        self.readonly_fields = fields
        return super(ShiftAdmin, self).get_form(request, obj, **kwargs)

    fields = [("time_start", "time_end"), "vendor", "valid", "payout"]

    list_display = ["time_start", "time_end", "vendor", "valid", "payout"]
    list_display_links = ["time_start"]
    list_filter = ["vendor", "valid", ("time_start", DateFieldListFilter)]

    search_fields = []

    ordering = ["-time_start"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent or request.user.is_financier

    def has_delete_permission(self, request, obj=None):
        return request.user.is_referent

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent or request.user.is_financier
