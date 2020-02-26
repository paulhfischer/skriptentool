import os

from django.contrib import admin

from core.models import Author, Balance, Cart, CartItem, CashBookEntry, Deposit, DepositNote, LectureNote, \
    PrintingQuota, Shift


def generate_cover(modeladmin, request, queryset):
    for lecturenote in queryset:
        if lecturenote.semester_end:
            semester = LectureNote.get_semester(lecturenote.semester_start)\
                       + " bis "\
                       + LectureNote.get_semester(lecturenote.semester_end)
        else:
            semester = LectureNote.get_semester(lecturenote.semester_start)

        pages = os.popen("pdfinfo " + lecturenote.file.path + " | grep 'Pages' | awk '{print $2}'").read().strip()
        template = open("media/deckblätter/vorlage/deckblatt.tex").read()
        content = template.replace("_studienzuschüsse_", str(lecturenote.study_grants))\
                          .replace("_author_", lecturenote.author.name)\
                          .replace("_title_", lecturenote.name)\
                          .replace("_semester_", semester)\
                          .replace("_price_", str(lecturenote.price).replace(".", ","))\
                          .replace("_pages_", pages)\
                          .replace("_ean_", lecturenote.ean)
        file = open("media/deckblätter/" + lecturenote.ean + ".tex", "w+")
        file.write(content)
        file.close()

        os.system("cd media/deckblätter;"
                  "latexmk -pdf " + lecturenote.ean + ".tex;"
                  "latexmk -c " + lecturenote.ean + ".tex;")
        os.system("cd media;"
                  "pdftk deckblätter/" + lecturenote.ean + ".pdf skripten/" + lecturenote.ean + ".pdf cat output druck/" + lecturenote.ean + ".pdf")


def generate_order(modeladmin, request, queryset):
    for lecturenote in queryset:
        if lecturenote.printnotes:
            printnotes = lecturenote.printnotes
        else:
            printnotes = ""

        template = open("media/skriptenaufträge/vorlage/skriptenauftrag.xfdf").read()
        content = template.replace("_file_", lecturenote.ean + ".pdf")\
                          .replace("_color_", LectureNote.get_color(lecturenote.color))\
                          .replace("_papersize_", LectureNote.get_papersize(lecturenote.papersize))\
                          .replace("_sides_", LectureNote.get_sides(lecturenote.sides))\
                          .replace("_amount_", "")\
                          .replace("_subject_", LectureNote.get_subject(lecturenote.subject))\
                          .replace("_printnotes_", printnotes)\
                          .replace("_name_", "")
        file = open("media/skriptenaufträge/" + lecturenote.ean + ".xfdf", "w+")
        file.write(content)
        file.close()

        os.system("cd media/skriptenaufträge;"
                  "pdftk vorlage/skriptenauftrag.pdf fill_form " + lecturenote.ean + ".xfdf output " + lecturenote.ean + ".pdf")


class CartItemInline(admin.StackedInline):
    fields = ["quantity"]
    model = CartItem


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
    actions = [generate_cover, generate_order]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["time_start", "time_end", "vendor", "valid", "payout"]
    list_filter = ["vendor", "valid"]
    list_editable = ["valid", "payout"]
    list_display_links = ["time_start"]
    ordering = ["-time_start"]


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
