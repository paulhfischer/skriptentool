from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models

import core.models.products
import core.models.user
import skriptentool.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128,
                        verbose_name="password",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="last login",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=256,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message=(
                                    "Lokale Benutzernamen müssen mit @ beginnen und dürfen nur "
                                    "Buchstaben enthalten."
                                ),
                                regex="@[a-z]+",
                            ),
                        ],
                        verbose_name="Benutzername",
                    ),
                ),
                (
                    "mail",
                    models.EmailField(
                        max_length=254,
                        verbose_name="E-Mail-Adresse",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        max_length=256,
                        verbose_name="Vorname",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=256,
                        verbose_name="Nachname",
                    ),
                ),
                (
                    "vendor",
                    models.BooleanField(
                        default=False,
                        verbose_name="Verkäufer",
                    ),
                ),
                (
                    "referent",
                    models.BooleanField(
                        default=False,
                        verbose_name="Referent",
                    ),
                ),
                (
                    "financier",
                    models.BooleanField(
                        default=False,
                        verbose_name="Finanzer",
                    ),
                ),
                (
                    "admin",
                    models.BooleanField(
                        default=False,
                        verbose_name="Admin",
                    ),
                ),
            ],
            options={
                "verbose_name": "Benutzer",
                "verbose_name_plural": "Benutzer",
                "ordering": ["username"],
            },
            managers=[
                ("objects", core.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=256,
                        verbose_name="Name",
                    ),
                ),
                (
                    "mail",
                    models.EmailField(
                        max_length=256,
                        verbose_name="E-Mail Adresse",
                    ),
                ),
            ],
            options={
                "verbose_name": "Autor",
                "verbose_name_plural": "Autoren",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Erstellzeitpunkt",
                    ),
                ),
                (
                    "vendor",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Verkäufer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Verkaufsvorgang",
                "verbose_name_plural": "Verkaufsvorgänge",
                "ordering": ["vendor"],
            },
        ),
        migrations.CreateModel(
            name="Deposit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ean",
                    models.CharField(
                        max_length=20,
                        validators=[
                            core.models.products.validate_ean,
                        ],
                        verbose_name="EAN",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=256,
                        verbose_name="Bezeichnung",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        verbose_name="Kautionsbetrag in Euro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kaution",
                "verbose_name_plural": "Kautionen",
                "ordering": ["ean"],
            },
        ),
        migrations.CreateModel(
            name="PrintingQuota",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ean",
                    models.CharField(
                        max_length=20,
                        validators=[
                            core.models.products.validate_ean,
                        ],
                        verbose_name="EAN",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        verbose_name="Preis in Euro",
                    ),
                ),
                (
                    "pages",
                    models.IntegerField(
                        verbose_name="Seitenzahl",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        verbose_name="Steht zum Verkauf",
                    ),
                ),
            ],
            options={
                "verbose_name": "Druckkontingent",
                "verbose_name_plural": "Druckkontingente",
                "ordering": ["ean"],
            },
        ),
        migrations.CreateModel(
            name="Shift",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time_start",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Verkaufsstart",
                    ),
                ),
                (
                    "time_end",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Verkaufsende",
                    ),
                ),
                (
                    "valid",
                    models.BooleanField(
                        default=False,
                        verbose_name="Überprüft",
                    ),
                ),
                (
                    "payout",
                    models.BooleanField(
                        default=False,
                        verbose_name="Getränke",
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Verkäufer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Verkaufsschicht",
                "verbose_name_plural": "Verkaufsschichten",
                "ordering": ["-time_start"],
            },
        ),
        migrations.CreateModel(
            name="LectureNote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ean",
                    models.CharField(
                        max_length=20,
                        validators=[
                            core.models.products.validate_ean,
                        ],
                        verbose_name="EAN",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=256,
                        verbose_name="Skriptname",
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        choices=[
                            ("M", "Mathematik"),
                            ("P", "Physik"),
                            ("I", "Informatik"),
                        ],
                        max_length=1,
                        verbose_name="Studiengang",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0")),
                        ],
                        verbose_name="Preis in Euro",
                    ),
                ),
                (
                    "study_grants",
                    models.BooleanField(
                        verbose_name="Studienzuschüsse",
                    ),
                ),
                (
                    "semester_start",
                    models.CharField(
                        choices=[
                            ("W2015", "Wintersemester 2015 / 2016"),
                            ("W2016", "Wintersemester 2016 / 2017"),
                            ("W2017", "Wintersemester 2017 / 2018"),
                            ("W2018", "Wintersemester 2018 / 2019"),
                            ("W2019", "Wintersemester 2019 / 2020"),
                            ("W2020", "Wintersemester 2020 / 2021"),
                            ("W2021", "Wintersemester 2021 / 2022"),
                            ("W2022", "Wintersemester 2022 / 2023"),
                            ("W2023", "Wintersemester 2023 / 2024"),
                            ("W2024", "Wintersemester 2024 / 2025"),
                            ("S2016", "Sommersemester 2016"),
                            ("S2017", "Sommersemester 2017"),
                            ("S2018", "Sommersemester 2018"),
                            ("S2019", "Sommersemester 2019"),
                            ("S2020", "Sommersemester 2020"),
                            ("S2021", "Sommersemester 2021"),
                            ("S2022", "Sommersemester 2022"),
                            ("S2023", "Sommersemester 2023"),
                            ("S2024", "Sommersemester 2024"),
                        ],
                        max_length=256,
                        verbose_name="Semester (von)",
                    ),
                ),
                (
                    "semester_end",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("W2015", "Wintersemester 2015 / 2016"),
                            ("W2016", "Wintersemester 2016 / 2017"),
                            ("W2017", "Wintersemester 2017 / 2018"),
                            ("W2018", "Wintersemester 2018 / 2019"),
                            ("W2019", "Wintersemester 2019 / 2020"),
                            ("W2020", "Wintersemester 2020 / 2021"),
                            ("W2021", "Wintersemester 2021 / 2022"),
                            ("W2022", "Wintersemester 2022 / 2023"),
                            ("W2023", "Wintersemester 2023 / 2024"),
                            ("W2024", "Wintersemester 2024 / 2025"),
                            ("S2016", "Sommersemester 2016"),
                            ("S2017", "Sommersemester 2017"),
                            ("S2018", "Sommersemester 2018"),
                            ("S2019", "Sommersemester 2019"),
                            ("S2020", "Sommersemester 2020"),
                            ("S2021", "Sommersemester 2021"),
                            ("S2022", "Sommersemester 2022"),
                            ("S2023", "Sommersemester 2023"),
                            ("S2024", "Sommersemester 2024"),
                        ],
                        max_length=256,
                        null=True,
                        verbose_name="Semester (bis)",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        verbose_name="Steht zum Verkauf",
                    ),
                ),
                (
                    "stock",
                    models.IntegerField(
                        default=0,
                        verbose_name="Bestand",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        blank=True,
                        choices=[
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
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Deckblattfarbe",
                    ),
                ),
                (
                    "papersize",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("A4_portrait", "A4 (Hochformat)"),
                            ("A4_landscape", "A4 (Querformat)"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Papiergröße",
                    ),
                ),
                (
                    "sides",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("simplex", "Einseitig"),
                            ("duplex", "Doppelseitig"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Seitigkeit",
                    ),
                ),
                (
                    "printnotes",
                    models.CharField(
                        blank=True,
                        max_length=256,
                        null=True,
                        verbose_name="Kommentar für Druck",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        storage=skriptentool.storage.OverwriteStorage(),
                        upload_to=core.models.products.get_filename,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["pdf"],
                            ),
                        ],
                        verbose_name="PDF-Datei",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.Author",
                        verbose_name="Autor",
                    ),
                ),
                (
                    "deposit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.Deposit",
                        verbose_name="Kaution",
                    ),
                ),
            ],
            options={
                "verbose_name": "Skript",
                "verbose_name_plural": "Skripten",
                "ordering": ["ean"],
            },
        ),
        migrations.CreateModel(
            name="DepositNote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        max_length=20,
                        verbose_name="Kautionsscheinnummer",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        verbose_name="Kautionsbetrag in Euro",
                    ),
                ),
                (
                    "sold_time",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Verkaufszeitpunkt",
                    ),
                ),
                (
                    "refunded_time",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Rückgabezeitpunkt",
                    ),
                ),
                (
                    "refundable",
                    models.BooleanField(
                        default=False,
                        verbose_name="Erstattbar",
                    ),
                ),
                (
                    "refunded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="refunded_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Zurückgegeben von",
                    ),
                ),
                (
                    "sold_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sold_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Verkauft von",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kautionsschein",
                "verbose_name_plural": "Kautionsscheine",
                "ordering": ["number"],
            },
        ),
        migrations.CreateModel(
            name="CashBookEntry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Zeitpunkt",
                    ),
                ),
                (
                    "detail",
                    models.CharField(
                        max_length=20,
                        verbose_name="Details",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        verbose_name="Betrag in Euro",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Ersteller",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kassenbucheintrag",
                "verbose_name_plural": "Kassenbucheinträge",
                "ordering": ["-time"],
            },
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ean",
                    models.CharField(
                        max_length=20,
                        verbose_name="EAN",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("lecturenote", "Skript"),
                            ("printingquota", "Druckkontingent"),
                            ("deposit", "Kautionsschein"),
                        ],
                        max_length=20,
                        verbose_name="Art",
                    ),
                ),
                (
                    "quantity",
                    models.IntegerField(
                        verbose_name="Anzahl",
                    ),
                ),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.Cart",
                        verbose_name="Verkaufsvorgang",
                    ),
                ),
            ],
            options={
                "verbose_name": "Artikel",
                "verbose_name_plural": "Artikel",
                "ordering": ["cart", "ean"],
            },
        ),
        migrations.CreateModel(
            name="Balance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Zeitpunkt",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        verbose_name="Kassenstand in Euro",
                    ),
                ),
                (
                    "counted",
                    models.BooleanField(
                        default=False,
                        verbose_name="Gezählt",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("initial", "Ersteinlage"),
                            ("opening", "Kassenbeginn"),
                            ("closing", "Kassenschluss"),
                            ("temporary", "Zwischenstand"),
                        ],
                        max_length=20,
                        verbose_name="Art",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Benutzer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kassenstand",
                "verbose_name_plural": "Kassenstände",
                "ordering": ["-time"],
            },
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.UniqueConstraint(
                fields=("ean", "cart"),
                name="unique_cart_item",
            ),
        ),
    ]
