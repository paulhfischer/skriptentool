from django.contrib import admin

from core.models import Author, Balance, Cart, CartItem, CashBookEntry, Deposit, DepositNote, LectureNote, \
    PrintingQuota, Shift


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ["ean", "name", "price"]
    list_filter = []
    list_editable = []
    list_display_links = ["ean"]
    ordering = ["-ean"]


@admin.register(PrintingQuota)
class PrintingQuotaAdmin(admin.ModelAdmin):
    list_display = ["ean", "pages", "price", "active"]
    list_filter = ["active"]
    list_editable = ["active"]
    list_display_links = ["ean"]
    ordering = ["-ean"]


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    list_display = ["ean", "name", "subject", "active", "stock", "printnotes"]
    list_filter = ["subject", "active"]
    list_editable = ["active", "stock", "printnotes"]
    list_display_links = ["ean"]
    ordering = ["-ean"]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["time_start", "time_end", "vendor", "valid", "payout"]
    list_filter = ["vendor", "valid"]
    list_editable = ["valid", "payout"]
    list_display_links = ["time_start"]
    ordering = ["-time_start"]


class CartItemInline(admin.StackedInline):
    fields = ["quantity"]
    model = CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["vendor", "time"]
    list_display_links = ["vendor"]
    ordering = ["-time"]
    inlines = [CartItemInline]


@admin.register(DepositNote)
class DepositNoteAdmin(admin.ModelAdmin):
    list_display = ["ean", "price", "sold_time", "sold_by", "refunded_time", "refunded_by"]
    list_display_links = ["ean"]
    ordering = ["-ean"]


@admin.register(CashBookEntry)
class CashBookEntryAdmin(admin.ModelAdmin):
    list_display = ["time", "user", "amount", "detail"]
    list_filter = ["user", "detail"]
    list_display_links = ["time"]
    ordering = ["-time"]


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ["time", "user", "amount", "type"]
    list_filter = ["type", "user"]
    list_editable = []
    list_display_links = ["time"]
    ordering = ["-time"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "mail"]
    list_display_links = ["name"]
    ordering = ["name"]
