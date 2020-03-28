from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = [
        ["Benutzdaten", {
            "fields": [("first_name", "last_name"), "username", "email"],
        }],
        ["Berechtigungen", {
            "fields": [("vendor", "referent", "financier", "admin")],
        }],
    ]

    # set editability of referent- financier- and admin-field depending on group
    def get_changelist(self, request, **kwargs):
        fields = []
        if request.user.is_financier:
            fields += ["financier"]
        if request.user.is_referent:
            fields += ["vendor", "referent"]
        if request.user.is_admin:
            fields += ["admin"]
        self.list_editable = fields
        return super(UserAdmin, self).get_changelist(request, **kwargs)

    # set editability of referent- financier- and admin-field depending on group
    def get_form(self, request, obj=None, **kwargs):
        fields = ['username', 'email', 'first_name', 'last_name']
        if not request.user.is_financier:
            fields += ["financier"]
        if not request.user.is_referent:
            fields += ["vendor", "referent"]
        if not request.user.is_admin:
            fields += ["admin"]
        self.readonly_fields = fields
        return super(UserAdmin, self).get_form(request, obj, **kwargs)

    list_display = ['get_full_name', 'username', 'vendor', 'referent', 'financier']
    list_display_links = ["get_full_name"]
    list_filter = ['vendor', 'referent', 'financier']

    search_fields = ["username"]

    ordering = ["username"]

    filter_horizontal = []

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent or request.user.is_financier

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent or request.user.is_financier
