from django.contrib import admin

from core.models import LectureNote, Cart, CartItem, Account, Author, Sale


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    list_display = ["ean", "name", "subject", "active", "stock", "printnotes"]
    list_filter = ["subject", "active"]
    list_editable = ["active", "stock", "printnotes"]
    list_display_links = ["ean"]
    ordering = ["-ean"]


class CartItemInline(admin.StackedInline):
    fields = ["quantity"]
    model = CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["vendor", "time"]
    list_display_links = ["vendor"]
    ordering = ["-time"]
    inlines = [CartItemInline]


@admin.register(Sale)
class CartAdmin(admin.ModelAdmin):
    list_display = ["time", "vendor", "ean", "price"]
    list_filter = ["ean", "vendor"]
    list_display_links = ["time"]
    ordering = ["-time"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["date", "changed_by", "balance", "type"]
    list_filter = ["type", "changed_by"]
    list_editable = []
    list_display_links = ["date"]
    ordering = ["-date"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "mail"]
    list_display_links = ["name"]
    ordering = ["name"]
