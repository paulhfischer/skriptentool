import os
import subprocess

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import FieldError

from SkriptenTool import settings
from core.models import Author, Deposit, DepositNote, LectureNote, PrintingQuota, Shift
from core.templatetags.filters import has_group
from core.utils.functions import get_pdf_page_count, tex_escape, xml_escape

admin.site.site_header = "SkriptenTool"
admin.site.site_title = "SkriptenTool"
admin.site.index_title = "Verwaltung"


def generate_cover(lecturenote):
    # generate semester-string (depending on range or single-semester)
    if lecturenote.semester_end:
        semester = LectureNote.get_semester(lecturenote.semester_start) \
                   + " bis " \
                   + LectureNote.get_semester(lecturenote.semester_end)
    else:
        semester = LectureNote.get_semester(lecturenote.semester_start)

    # open latex-template for covers
    with open(settings.COVER_TEMPLATE_FILE) as f:
        template = f.read()

    # replace placeholders in template
    content = template.replace("_studygrants_", tex_escape(lecturenote.study_grants)) \
                      .replace("_author_", tex_escape(lecturenote.author.name)) \
                      .replace("_title_", tex_escape(lecturenote.name)) \
                      .replace("_semester_", tex_escape(semester)) \
                      .replace("_price_", tex_escape(str(intcomma(lecturenote.price)))) \
                      .replace("_pages_", tex_escape(get_pdf_page_count(lecturenote.file.path))) \
                      .replace("_ean_", tex_escape(lecturenote.ean))

    with open(os.path.join(settings.COVERS_DIR, lecturenote.ean + ".tex"), "w+") as f:
        f.write(content)

    # run bash script to generate cover
    return subprocess.run(["core/utils/generate_cover.sh", lecturenote.ean, settings.COVERS_DIR, settings.LECTURE_NOTES_DIR, settings.OUTPUT_DIR])\
                     .returncode == 0


def generate_order(lecturenote):
    # open xfdf-template for orders
    with open(settings.ORDER_TEMPLATE_CONTENT_FILE) as f:
        template = f.read()

    # replace placeholders in template
    content = template.replace("_file_", xml_escape(lecturenote.ean + ".pdf")) \
                      .replace("_color_", xml_escape(LectureNote.get_color(lecturenote.color))) \
                      .replace("_papersize_", xml_escape(LectureNote.get_papersize(lecturenote.papersize))) \
                      .replace("_sides_", xml_escape(LectureNote.get_sides(lecturenote.sides))) \
                      .replace("_amount_", xml_escape("")) \
                      .replace("_subject_", xml_escape(LectureNote.get_subject(lecturenote.subject))) \
                      .replace("_printnotes_", xml_escape(lecturenote.printnotes or "")) \
                      .replace("_name_", xml_escape(""))

    with open(os.path.join(settings.ORDERS_DIR, lecturenote.ean + ".xfdf"), "w+") as f:
        f.write(content)

    # run bash script to generate order
    return subprocess.run(["core/utils/generate_order.sh", lecturenote.ean, settings.ORDERS_DIR, settings.ORDER_TEMPLATE_FORM_FILE])\
                     .returncode == 0


def update_files(ean_old, ean_new):
    lecturenote = LectureNote.objects.get(ean=ean_new)

    # return true and change path in model if rename successfull, return false otherwise
    if subprocess.run(["core/utils/rename_files.sh", ean_old, ean_new, settings.COVERS_DIR, settings.OUTPUT_DIR, settings.LECTURE_NOTES_DIR,
                       settings.ORDERS_DIR]).returncode == 0:
        lecturenote.file = os.path.relpath(os.path.join(settings.LECTURE_NOTES_DIR, ean_new + ".pdf"), settings.BASE_DIR)
        lecturenote.save()
        return True
    else:
        return False


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

        # rename files if ean has changed
        if change and "ean" in form.changed_data:
            if not update_files(form.initial["ean"], obj.ean):
                raise FieldError("Umbennenung der Skripten ist fehlgeschlagen")

        # generate new cover if value printed on cover has changed
        if any(item in ["study_grants", "author", "name", "semester_start", "semester_end", "price", "file", "ean"] for item in form.changed_data):
            if not generate_cover(obj):
                raise FieldError("Generierung des Deckblatts ist fehlgeschlagen!")

        # generate new order if value printed on order has changed
        if any(item in ["ean", "color", "papersize", "sides", "subject", "printnotes"] for item in form.changed_data):
            if not generate_order(obj):
                raise FieldError("Generierung des Skriptenauftrags ist fehlgeschlagen!")

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
    # set editability of payout- and valid-field depending on group
    def get_changelist(self, request, **kwargs):
        fields = []
        if has_group(request.user, "Finanzer"):
            fields += ["payout"]
        if has_group(request.user, "Referent"):
            fields += ["valid"]
        self.list_editable = fields
        return super(ShiftAdmin, self).get_changelist(request, **kwargs)

    # set editability of payout- and valid-field depending on group
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
    list_filter = ["vendor", "valid", ("time_start", DateFieldListFilter)]

    search_fields = []

    ordering = ["-time_start"]


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


class LectureNoteInline(admin.StackedInline):
    model = LectureNote
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True

    fields = [("subject", "active")]
    readonly_fields = ["ean", "name", "subject", "active"]


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
