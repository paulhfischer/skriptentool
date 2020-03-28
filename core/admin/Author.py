from django.contrib import admin

from core.models import Author, LectureNote


class LectureNoteInline(admin.StackedInline):
    model = LectureNote
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True

    fields = [("subject", "active")]
    readonly_fields = ["ean", "name", "subject", "active"]

    def has_add_permission(self, request):
        return request.user.is_referent

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent

    def has_delete_permission(self, request, obj=None):
        return request.user.is_referent

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fields = ["name", "mail"]
    readonly_fields = []

    list_display = ["name", "mail"]
    list_display_links = ["name"]
    list_editable = []
    list_filter = []

    search_fields = ["name"]

    ordering = ["name"]

    inlines = [LectureNoteInline]

    def has_add_permission(self, request):
        return request.user.is_referent

    def has_change_permission(self, request, obj=None):
        return request.user.is_referent

    def has_delete_permission(self, request, obj=None):
        return request.user.is_referent

    def has_view_permission(self, request, obj=None):
        return request.user.is_referent
