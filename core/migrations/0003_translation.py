from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models

import core.models.products
import skriptentool.storage


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_cashbookentry_comments"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="author",
            options={
                "ordering": ["name"],
                "verbose_name": "author",
                "verbose_name_plural": "authors",
            },
        ),
        migrations.AlterModelOptions(
            name="balance",
            options={
                "ordering": ["-time"],
                "verbose_name": "balance",
                "verbose_name_plural": "balances",
            },
        ),
        migrations.AlterModelOptions(
            name="cart",
            options={
                "ordering": ["vendor"],
                "verbose_name": "cart",
                "verbose_name_plural": "carts",
            },
        ),
        migrations.AlterModelOptions(
            name="cartitem",
            options={
                "ordering": ["cart", "ean"],
                "verbose_name": "item",
                "verbose_name_plural": "items",
            },
        ),
        migrations.AlterModelOptions(
            name="cashbookentry",
            options={
                "ordering": ["-time"],
                "verbose_name": "cash book entry",
                "verbose_name_plural": "cash book entries",
            },
        ),
        migrations.AlterModelOptions(
            name="deposit",
            options={
                "ordering": ["ean"],
                "verbose_name": "deposit",
                "verbose_name_plural": "deposits",
            },
        ),
        migrations.AlterModelOptions(
            name="depositnote",
            options={
                "ordering": ["number"],
                "verbose_name": "deposit note",
                "verbose_name_plural": "deposit notes",
            },
        ),
        migrations.AlterModelOptions(
            name="lecturenote",
            options={
                "ordering": ["ean"],
                "verbose_name": "lecture note",
                "verbose_name_plural": "lecture notes",
            },
        ),
        migrations.AlterModelOptions(
            name="printingquota",
            options={
                "ordering": ["ean"],
                "verbose_name": "printing quota",
                "verbose_name_plural": "printing quotas",
            },
        ),
        migrations.AlterModelOptions(
            name="shift",
            options={
                "ordering": ["-time_start"],
                "verbose_name": "sales shift",
                "verbose_name_plural": "sales shifts",
            },
        ),
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ["username"],
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
        ),
        migrations.AlterField(
            model_name="author",
            name="mail",
            field=models.EmailField(
                max_length=256,
                verbose_name="mail",
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="name",
            field=models.CharField(
                max_length=256,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="balance",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=6,
                verbose_name="amount (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="balance",
            name="counted",
            field=models.BooleanField(
                default=False,
                verbose_name="counted",
            ),
        ),
        migrations.AlterField(
            model_name="balance",
            name="time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="time",
            ),
        ),
        migrations.AlterField(
            model_name="balance",
            name="type",
            field=models.CharField(
                choices=[
                    ("initial", "initial"),
                    ("opening", "opening"),
                    ("closing", "closing"),
                    ("temporary", "temporary"),
                ],
                max_length=20,
                verbose_name="type",
            ),
        ),
        migrations.AlterField(
            model_name="balance",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="cart",
            name="time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="time of creation",
            ),
        ),
        migrations.AlterField(
            model_name="cart",
            name="vendor",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="vendor",
            ),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="cart",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="core.Cart",
                verbose_name="cart",
            ),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="quantity",
            field=models.IntegerField(
                verbose_name="quantity",
            ),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="type",
            field=models.CharField(
                choices=[
                    ("lecturenote", "lecture note"),
                    ("printingquota", "printing quota"),
                    ("deposit", "deposit"),
                ],
                max_length=20,
                verbose_name="type",
            ),
        ),
        migrations.AlterField(
            model_name="cashbookentry",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=6,
                verbose_name="amount (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="cashbookentry",
            name="detail",
            field=models.CharField(
                max_length=256,
                verbose_name="detail",
            ),
        ),
        migrations.AlterField(
            model_name="cashbookentry",
            name="time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="time",
            ),
        ),
        migrations.AlterField(
            model_name="cashbookentry",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="deposit",
            name="name",
            field=models.CharField(
                max_length=256,
                verbose_name="designation",
            ),
        ),
        migrations.AlterField(
            model_name="deposit",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                verbose_name="deposit amount (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="number",
            field=models.CharField(
                max_length=20,
                verbose_name="number",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                verbose_name="deposit (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="refundable",
            field=models.BooleanField(
                default=False,
                verbose_name="refundable",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="refunded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="refunded_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="refunded by",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="refunded_time",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="return time",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="sold_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sold_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="sold by",
            ),
        ),
        migrations.AlterField(
            model_name="depositnote",
            name="sold_time",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="time of sale",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="active",
            field=models.BooleanField(
                verbose_name="for sale",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.Author",
                verbose_name="author",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="color",
            field=models.CharField(
                blank=True,
                choices=[
                    ("royal blue", "royal blue"),
                    ("ice_blue", "ice blue"),
                    ("caribbean_blue", "caribbean blue"),
                    ("sea_green", "sea green"),
                    ("grass_green", "grass green"),
                    ("may_green", "may green"),
                    ("grey", "grey"),
                    ("fuchsia", "fuchsia"),
                    ("purple", "purple"),
                    ("violet", "violet"),
                    ("brick_red", "brick red"),
                    ("pink", "pink"),
                    ("lachs", "salmon"),
                    ("orange", "orange"),
                    ("camel", "camel"),
                    ("light_yellow", "light yellow"),
                    ("golden_yellow", "golden yellow"),
                    ("chamois", "chamois"),
                ],
                max_length=20,
                null=True,
                verbose_name="color of cover",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="deposit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.Deposit",
                verbose_name="deposit",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="file",
            field=models.FileField(
                storage=skriptentool.storage.OverwriteStorage(),
                upload_to=core.models.products.get_filename,
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=["pdf"]),
                ],
                verbose_name="PDF file",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="name",
            field=models.CharField(
                max_length=256,
                verbose_name="designation",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="papersize",
            field=models.CharField(
                blank=True,
                choices=[
                    ("A4_portrait", "A4 (portrait)"),
                    ("A4_landscape", "A4 (landscape)"),
                ],
                max_length=20,
                null=True,
                verbose_name="papersize",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0")),
                ],
                verbose_name="price (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="printnotes",
            field=models.CharField(
                blank=True,
                max_length=256,
                null=True,
                verbose_name="notes for printing",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="semester_end",
            field=models.CharField(
                blank=True,
                choices=[
                    ("S2025", "summer term 2025"),
                    ("W2024", "winter term 2024 / 2025"),
                    ("S2024", "summer term 2024"),
                    ("W2023", "winter term 2023 / 2024"),
                    ("S2023", "summer term 2023"),
                    ("W2022", "winter term 2022 / 2023"),
                    ("S2022", "summer term 2022"),
                    ("W2021", "winter term 2021 / 2022"),
                    ("S2021", "summer term 2021"),
                    ("W2020", "winter term 2020 / 2021"),
                    ("S2020", "summer term 2020"),
                    ("W2019", "winter term 2019 / 2020"),
                    ("S2019", "summer term 2019"),
                    ("W2018", "winter term 2018 / 2019"),
                    ("S2018", "summer term 2018"),
                    ("W2017", "winter term 2017 / 2018"),
                    ("S2017", "summer term 2017"),
                    ("W2016", "winter term 2016 / 2017"),
                    ("S2016", "summer term 2016"),
                    ("W2015", "winter term 2015 / 2016"),
                ],
                max_length=256,
                null=True,
                verbose_name="semester (end)",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="semester_start",
            field=models.CharField(
                choices=[
                    ("S2025", "summer term 2025"),
                    ("W2024", "winter term 2024 / 2025"),
                    ("S2024", "summer term 2024"),
                    ("W2023", "winter term 2023 / 2024"),
                    ("S2023", "summer term 2023"),
                    ("W2022", "winter term 2022 / 2023"),
                    ("S2022", "summer term 2022"),
                    ("W2021", "winter term 2021 / 2022"),
                    ("S2021", "summer term 2021"),
                    ("W2020", "winter term 2020 / 2021"),
                    ("S2020", "summer term 2020"),
                    ("W2019", "winter term 2019 / 2020"),
                    ("S2019", "summer term 2019"),
                    ("W2018", "winter term 2018 / 2019"),
                    ("S2018", "summer term 2018"),
                    ("W2017", "winter term 2017 / 2018"),
                    ("S2017", "summer term 2017"),
                    ("W2016", "winter term 2016 / 2017"),
                    ("S2016", "summer term 2016"),
                    ("W2015", "winter term 2015 / 2016"),
                ],
                max_length=256,
                verbose_name="semester (start)",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="sides",
            field=models.CharField(
                blank=True,
                choices=[
                    ("simplex", "one-sided"),
                    ("duplex", "two-sided"),
                ],
                max_length=20,
                null=True,
                verbose_name="sides",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="stock",
            field=models.IntegerField(
                default=0,
                verbose_name="stock",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="study_grants",
            field=models.BooleanField(
                verbose_name="study grants",
            ),
        ),
        migrations.AlterField(
            model_name="lecturenote",
            name="subject",
            field=models.CharField(
                choices=[
                    ("M", "mathematics"),
                    ("P", "physics"),
                    ("I", "informatics"),
                ],
                max_length=1,
                verbose_name="subject",
            ),
        ),
        migrations.AlterField(
            model_name="printingquota",
            name="active",
            field=models.BooleanField(
                verbose_name="for sale",
            ),
        ),
        migrations.AlterField(
            model_name="printingquota",
            name="pages",
            field=models.IntegerField(
                verbose_name="number of pages",
            ),
        ),
        migrations.AlterField(
            model_name="printingquota",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                verbose_name="price (in €)",
            ),
        ),
        migrations.AlterField(
            model_name="shift",
            name="payout",
            field=models.BooleanField(
                default=False,
                verbose_name="beverages",
            ),
        ),
        migrations.AlterField(
            model_name="shift",
            name="time_end",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="end time",
            ),
        ),
        migrations.AlterField(
            model_name="shift",
            name="time_start",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="start time",
            ),
        ),
        migrations.AlterField(
            model_name="shift",
            name="valid",
            field=models.BooleanField(
                default=False,
                verbose_name="reviewed",
            ),
        ),
        migrations.AlterField(
            model_name="shift",
            name="vendor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="vendor",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="admin",
            field=models.BooleanField(
                default=False,
                verbose_name="admin",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="financier",
            field=models.BooleanField(
                default=False,
                verbose_name="financier",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                max_length=256,
                verbose_name="first name",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                max_length=256,
                verbose_name="last name",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="mail",
            field=models.EmailField(
                max_length=254,
                verbose_name="mail",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="referent",
            field=models.BooleanField(
                default=False,
                verbose_name="referent",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                max_length=256,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message=(
                            'Local usernames have to start with "@" and may only contain letters.'
                        ),
                        regex="@[a-z]+",
                    ),
                ],
                verbose_name="username",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="vendor",
            field=models.BooleanField(
                default=False,
                verbose_name="vendor",
            ),
        ),
    ]
