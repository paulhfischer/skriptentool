import os

from django.contrib import admin

from core.models import Author, Deposit, DepositNote, LectureNote, PrintingQuota, Shift
from core.templatetags.filters import has_group

admin.site.site_header = "SkriptenTool"
admin.site.site_title = "SkriptenTool"
admin.site.index_title = "Verwaltung"


def generate_cover(lecturenote):
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


def generate_order(lecturenote):
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


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    fields = ["ean", "name", "price"]
    readonly_fields = ["ean"]

    list_display = ["ean", "name", "price"]
    list_display_links = ["ean"]
    list_editable = []
    list_filter = []

    search_fields = ["ean"]

    ordering = ["-ean"]


@admin.register(PrintingQuota)
class PrintingQuotaAdmin(admin.ModelAdmin):
    fields = ["ean", "pages", "price", "active"]
    readonly_fields = ["ean"]

    list_display = ["ean", "pages", "price", "active"]
    list_display_links = ["ean"]
    list_editable = ["active"]
    list_filter = ["active"]

    search_fields = ["ean"]

    ordering = ["-ean"]


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        generate_cover(obj)
        generate_order(obj)
        super(LectureNoteAdmin, self).save_model(request, obj, form, change)

    fieldsets = [
        [None, {
            "fields": ["ean", ("stock", "active")],
        }],
        ["Eigenschaften", {
            "fields": ["name", "subject", ("price", "study_grants"), "author", ("semester_start", "semester_end"), "deposit"],
        }],
        ["Druckeinstellungen", {
            "fields": ["color", "papersize", "sides", "printnotes", "file"],
        }],
    ]
    readonly_fields = ["ean"]

    list_display = ["ean", "name", "subject", "active", "stock", "printnotes"]
    list_display_links = ["ean"]
    list_editable = ["active", "stock", "printnotes"]
    list_filter = ["subject", "active"]

    search_fields = ["ean"]

    ordering = ["-ean"]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        fields = []
        if has_group(request.user, "Finanzer"):
            fields += ["payout"]
        if has_group(request.user, "Referent"):
            fields += ["valid"]
        self.list_editable = fields
        return super(ShiftAdmin, self).get_changelist(request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        fields = ["time_start", "time_end"]
        if not has_group(request.user, "Finanzer"):
            fields += ["payout"]
        if not has_group(request.user, "Referent"):
            fields += ["valid"]
        self.readonly_fields = fields
        return super(ShiftAdmin, self).get_form(request, obj, **kwargs)

    fields = [("time_start", "time_end"), "vendor", "valid", "payout"]

    list_display = ["time_start", "time_end", "vendor", "valid", "payout"]
    list_display_links = ["time_start"]
    list_filter = ["vendor", "valid"]

    search_fields = []

    ordering = ["-time_start"]


@admin.register(DepositNote)
class DepositNoteAdmin(admin.ModelAdmin):
    fields = ["ean", "price", ("sold_time", "sold_by"), ("refunded_time", "refunded_by"), "refundable"]
    readonly_fields = ["ean", "price", "sold_time", "sold_by", "refunded_time", "refunded_by"]

    list_display = ["ean", "price", "sold_time", "refunded_time", "refundable"]
    list_display_links = ["ean"]
    list_editable = ["refundable"]
    list_filter = ["refundable"]

    search_fields = ["ean"]

    ordering = ["-ean"]


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
