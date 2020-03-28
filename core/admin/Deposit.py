from django.contrib import admin

from core.models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    fields = ["ean", "name", "price"]
    readonly_fields = []

    list_display = ["ean", "name", "price"]
    list_display_links = ["ean"]
    list_editable = []
    list_filter = []

    search_fields = ["ean"]

    ordering = ["-ean"]
