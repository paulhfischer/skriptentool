import os
import subprocess  # nosec
from decimal import Decimal

from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.db import models

from core.models import Author
from core.utils.functions import get_pdf_page_count
from core.utils.functions import get_semesters
from core.utils.functions import tex_escape
from core.utils.functions import xml_escape
from skriptentool import settings
from skriptentool.storage import OverwriteStorage


# return model instance from ean
def get_product(ean):
    ean = str(ean)
    if LectureNote.objects.filter(ean=ean).exists():
        return LectureNote.objects.get(ean=ean)
    elif PrintingQuota.objects.filter(ean=ean).exists():
        return PrintingQuota.objects.get(ean=ean)
    elif Deposit.objects.filter(ean=ean).exists():
        return Deposit.objects.get(ean=ean)

    raise ObjectDoesNotExist(f"Es konnte kein Produkt mit der EAN {ean} gefunden werden.")


# return model type from ean
def get_type(ean):
    return type(get_product(ean)).__name__.lower()


def generate_cover(lecturenote):
    # generate semester-string (depending on range or single-semester)
    if lecturenote.semester_end:
        semester = (
            f"{lecturenote.get_semester_start_display()} bis "
            f"{lecturenote.get_semester_end_display()}"
        )
    else:
        semester = lecturenote.get_semester_start_display()

    # open latex-template for covers
    with open(settings.COVER_TEMPLATE_FILE) as f:
        template = f.read()

    # replace placeholders in template
    content = (
        template.replace("_studygrants_", tex_escape(lecturenote.study_grants))
        .replace("_author_", tex_escape(getattr(lecturenote.author, "name", "")))
        .replace("_title_", tex_escape(lecturenote.name))
        .replace("_semester_", tex_escape(semester))
        .replace("_price_", tex_escape(str(intcomma(lecturenote.price))))
        .replace("_pages_", tex_escape(get_pdf_page_count(lecturenote.file.path)))
        .replace("_ean_", tex_escape(lecturenote.ean))
    )

    with open(os.path.join(settings.COVERS_DIR, f"{lecturenote.ean}.tex"), "w+") as f:
        f.write(content)

    # run bash script to generate cover
    return (
        subprocess.run(  # nosec
            [
                "core/utils/generate_cover.sh",
                lecturenote.ean,
                settings.COVERS_DIR,
                settings.LECTURE_NOTES_DIR,
                settings.OUTPUT_DIR,
            ],
            capture_output=True,
        )
        .stderr.decode("utf-8")
        .splitlines()
    )


def generate_order(lecturenote):
    # open xfdf-template for orders
    with open(settings.ORDER_TEMPLATE_CONTENT_FILE) as f:
        template = f.read()

    # replace placeholders in template
    content = (
        template.replace("_file_", xml_escape(f"{lecturenote.ean}.pdf"))
        .replace("_color_", xml_escape(lecturenote.get_color_display() or ""))
        .replace("_papersize_", xml_escape(lecturenote.get_papersize_display() or ""))
        .replace("_sides_", xml_escape(lecturenote.get_sides_display() or ""))
        .replace("_amount_", xml_escape(""))
        .replace("_subject_", xml_escape(lecturenote.get_subject_display()))
        .replace("_printnotes_", xml_escape(lecturenote.printnotes or ""))
        .replace("_name_", xml_escape(""))
    )

    with open(os.path.join(settings.ORDERS_DIR, f"{lecturenote.ean}.xfdf"), "w+") as f:
        f.write(content)

    # run bash script to generate order
    return (
        subprocess.run(  # nosec
            [
                "core/utils/generate_order.sh",
                lecturenote.ean,
                settings.ORDERS_DIR,
                settings.ORDER_TEMPLATE_FORM_FILE,
            ],
            capture_output=True,
        )
        .stderr.decode("utf-8")
        .splitlines()
    )


def update_files(ean_old, ean_new, lecturenote):
    process = subprocess.run(  # nosec
        [
            "core/utils/rename_files.sh",
            ean_old,
            ean_new,
            settings.COVERS_DIR,
            settings.OUTPUT_DIR,
            settings.LECTURE_NOTES_DIR,
            settings.ORDERS_DIR,
        ],
        capture_output=True,
    )

    # change path in model if rename successfull
    if process.returncode == 0:
        lecturenote.file = os.path.relpath(
            os.path.join(settings.LECTURE_NOTES_DIR, f"{ean_new}.pdf"),
            settings.MEDIA_ROOT,
        )
        super(LectureNote, lecturenote).save()

    # return errors
    return process.stderr.decode("utf-8").splitlines()


# return path to lecturenote-pdf, relative to media folder
def get_filename(instance, filename):
    return os.path.join(
        os.path.relpath(settings.LECTURE_NOTES_DIR, settings.MEDIA_ROOT),
        f"{instance.ean}.pdf",
    )


# check if input is value for form validation
def validate_ean(value):
    if not value.isdigit():
        raise ValidationError("EANs dürfen nur aus Zahlen bestehen.")


# check of input ean already exists for form validation
# necessary as products are different models but need distinct eans
def ean_unique(obj, model, exclude):
    errors = {}
    try:
        super(model, obj).clean_fields(exclude)
    except ValidationError as e:
        errors.update(e)

    if (
        LectureNote.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists()
        or PrintingQuota.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists()
        or Deposit.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists()
    ):
        errors.update({"ean": ["Ein Artikel mit dieser EAN existiert bereits."]})

    if errors:
        raise ValidationError(errors)


class Deposit(models.Model):
    class Meta:
        verbose_name = "Kaution"
        verbose_name_plural = "Kautionen"
        ordering = ["ean"]

    active = True

    ean = models.CharField(
        max_length=20,
        verbose_name="EAN",
        validators=[validate_ean],
    )

    name = models.CharField(
        max_length=256,
        verbose_name="Bezeichnung",
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Kautionsbetrag in Euro",
    )

    def __str__(self):
        return f"{self.name} ({self.ean})"

    def clean_fields(self, exclude=None):
        # overwrite validation function to check if ean is unique accros all products
        ean_unique(self, Deposit, exclude)

    permissions = {
        "list": {
            "is_referent": "__all__",
        },
        "create": {
            "is_referent": "__all__",
        },
        "update": {
            "is_referent": "__all__",
        },
        "delete": [
            "is_referent",
        ],
    }


class LectureNote(models.Model):
    class Meta:
        verbose_name = "Skript"
        verbose_name_plural = "Skripten"
        ordering = ["ean"]

    SUBJECTS = [
        ("M", "Mathematik"),
        ("P", "Physik"),
        ("I", "Informatik"),
    ]

    COLORS = [
        ("royalblau", "Royalblau"),
        ("eisblau", "Eisblau"),
        ("karibikblau", "Karibikblau"),
        ("seegrün", "Seegrün"),
        ("grasgrün", "Grasgrün"),
        ("maigrün", "Maigrün"),
        ("grau", "Grau"),
        ("fuchsia", "Fuchsia"),
        ("lila", "Lila"),
        ("violett", "Violett"),
        ("ziegelrot", "Ziegelrot"),
        ("rosa", "Rosa"),
        ("lachs", "Lachs"),
        ("orange", "Orange"),
        ("camel", "Camel"),
        ("hellgelb", "Hellgelb"),
        ("goldgelb", "Goldgelb"),
        ("chamois", "Chamois"),
    ]

    PAPERSIZES = [
        ("A4_portrait", "A4 (Hochformat)"),
        ("A4_landscape", "A4 (Querformat)"),
    ]

    SIDES = [
        ("simplex", "Einseitig"),
        ("duplex", "Doppelseitig"),
    ]

    # IMPORTANT: semesters have to be updated manually
    SEMESTERS = get_semesters("W2015", "S2025")

    ean = models.CharField(
        max_length=20,
        validators=[validate_ean],
        verbose_name="EAN",
    )

    name = models.CharField(
        max_length=256,
        verbose_name="Skriptname",
    )

    subject = models.CharField(
        max_length=1,
        choices=SUBJECTS,
        verbose_name="Studiengang",
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.00))],
        verbose_name="Preis in Euro",
    )

    study_grants = models.BooleanField(
        verbose_name="Studienzuschüsse",
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Autor",
    )

    semester_start = models.CharField(
        max_length=256,
        choices=SEMESTERS,
        verbose_name="Semester (von)",
    )

    semester_end = models.CharField(
        max_length=256,
        choices=SEMESTERS,
        blank=True,
        null=True,
        verbose_name="Semester (bis)",
    )

    active = models.BooleanField(
        verbose_name="Steht zum Verkauf",
    )

    deposit = models.ForeignKey(
        Deposit,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Kaution",
    )

    stock = models.IntegerField(
        default=0,
        verbose_name="Bestand",
    )

    color = models.CharField(
        max_length=20,
        choices=COLORS,
        blank=True,
        null=True,
        verbose_name="Deckblattfarbe",
    )

    papersize = models.CharField(
        max_length=20,
        choices=PAPERSIZES,
        blank=True,
        null=True,
        verbose_name="Papiergröße",
    )

    sides = models.CharField(
        max_length=20,
        choices=SIDES,
        blank=True,
        null=True,
        verbose_name="Seitigkeit",
    )

    printnotes = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Kommentar für Druck",
    )

    file = models.FileField(
        upload_to=get_filename,
        storage=OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="PDF-Datei",
    )

    def __str__(self):
        return f"{self.name} ({self.ean})"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # store orignal fieldvalue to check if value has changed
        for field in self._meta.get_fields():
            setattr(self, f"__original_{field.name}", getattr(self, field.name))

    def changed_fields(self):
        # get list of changed fields
        changed_fields = []
        for field in self._meta.get_fields():
            if getattr(self, field.name) != getattr(self, f"__original_{field.name}"):
                changed_fields.append(field.name)
        return changed_fields

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        update = not self._state.adding

        super(LectureNote, self).save(force_insert, force_update, using, update_fields)

        # rename files if ean has changed and model not newly created
        if update and "ean" in self.changed_fields():
            errors = update_files(getattr(self, "__original_ean"), self.ean, self)
            if errors:
                raise ValidationError(errors)

        # generate new cover if value printed on cover has changed
        if any(
            item
            in [
                "study_grants",
                "author",
                "name",
                "semester_start",
                "semester_end",
                "price",
                "file",
                "ean",
            ]
            for item in self.changed_fields()
        ):

            errors = generate_cover(self)
            if errors:
                raise ValidationError(errors)

        # generate new order if value printed on order has changed
        if any(
            item in ["ean", "color", "papersize", "sides", "subject", "printnotes"]
            for item in self.changed_fields()
        ):

            errors = generate_order(self)
            if errors:
                raise ValidationError(errors)

    def clean_fields(self, exclude=None):
        # overwrite validation function to check if ean is unique accros all products
        ean_unique(self, LectureNote, exclude)

    permissions = {
        "list": {
            "is_referent": "__all__",
        },
        "create": {
            "is_referent": "__all__",
        },
        "update": {
            "is_referent": "__all__",
        },
        "delete": [
            "is_referent",
        ],
    }


class PrintingQuota(models.Model):
    class Meta:
        verbose_name = "Druckkontingent"
        verbose_name_plural = "Druckkontingente"
        ordering = ["ean"]

    ean = models.CharField(
        max_length=20,
        validators=[validate_ean],
        verbose_name="EAN",
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Preis in Euro",
    )

    pages = models.IntegerField(
        verbose_name="Seitenzahl",
    )

    active = models.BooleanField(
        verbose_name="Steht zum Verkauf",
    )

    def __str__(self):
        return f"{self.pages} Seiten ({self.ean})"

    def clean_fields(self, exclude=None):
        # overwrite validation function to check if ean is unique across all products
        ean_unique(self, PrintingQuota, exclude)

    @property
    def name(self):
        return f"{self.pages} Seiten"

    permissions = {
        "list": {
            "is_referent": "__all__",
        },
        "create": {
            "is_referent": "__all__",
        },
        "update": {
            "is_referent": "__all__",
        },
        "delete": [
            "is_referent",
        ],
    }
