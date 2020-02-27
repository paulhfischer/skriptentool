import os

from django import forms
from django.contrib import admin

from core.models import Author, Deposit, DepositNote, LectureNote, PrintingQuota, Shift
from core.templatetags.filters import has_group

import subprocess

admin.site.site_header = "SkriptenTool"
admin.site.site_title = "SkriptenTool"
admin.site.index_title = "Verwaltung"


COVERS_DIR                        = "media/deckblätter"
LECTURE_NOTES_DIR                 = "media/skripten"
ORDERS_DIR                        = "media/skriptenaufträge"
OUTPUT_DIR                        = "media/druck"
COVER_TEMPLATE_FILE               = os.path.join(COVERS_DIR, "vorlage/deckblatt.tex")
LECTURE_NOTES_ORDER_TEMPLATE_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.xfdf")


def get_pdf_page_count(path):
    output = subprocess.run(['pdfinfo', path], stdout=subprocess.PIPE).stdout.decode()
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return line.split(":")[1].strip()

    return "Unknown"


def generate_cover(lecturenote):
    if lecturenote.semester_end:
        semester = LectureNote.get_semester(lecturenote.semester_start)\
                   + " bis "\
                   + LectureNote.get_semester(lecturenote.semester_end)
    else:
        semester = LectureNote.get_semester(lecturenote.semester_start)

    with open(COVER_TEMPLATE_FILE, "r") as f:
        template = f.read()

    content = template.replace("_studienzuschüsse_", str(lecturenote.study_grants))\
                      .replace("_author_", lecturenote.author.name)\
                      .replace("_title_", lecturenote.name)\
                      .replace("_semester_", semester)\
                      .replace("_price_", str(lecturenote.price).replace(".", ","))\
                      .replace("_pages_", get_pdf_page_count(lecturenote.file.path))\
                      .replace("_ean_", lecturenote.ean)

    with open(os.path.join(COVERS_DIR, lecturenote.ean + ".tex"), "w+") as f:
        f.write(content)

    return subprocess.run(['./contrib/generate_cover.sh', lecturenote.ean]).returncode == 0


def generate_order(lecturenote):
    with open(LECTURE_NOTES_ORDER_TEMPLATE_FILE, "r") as f:
        template = f.read()

    content = template.replace("_file_", lecturenote.ean + ".pdf")\
                      .replace("_color_", LectureNote.get_color(lecturenote.color))\
                      .replace("_papersize_", LectureNote.get_papersize(lecturenote.papersize))\
                      .replace("_sides_", LectureNote.get_sides(lecturenote.sides))\
                      .replace("_amount_", "")\
                      .replace("_subject_", LectureNote.get_subject(lecturenote.subject))\
                      .replace("_printnotes_", lecturenote.printnotes or "")\
                      .replace("_name_", "")

    with open(os.path.join(ORDERS_DIR, lecturenote.ean + ".xfdf"), "w+") as f:
        f.write(content)

    return subprocess.run(['./contrib/generate_order.sh', lecturenote.ean]).returncode == 0


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


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(LectureNoteAdmin, self).save_model(request, obj, form, change)

        if not generate_cover(obj):
            raise forms.ValidationError("Error while generating cover")

        if not generate_order(obj):
            raise forms.ValidationError("Error while generating order")

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
    readonly_fields = []

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
