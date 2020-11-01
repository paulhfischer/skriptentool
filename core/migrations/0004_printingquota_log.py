import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_translation"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrintingQuotaLog",
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
                        verbose_name="time",
                    ),
                ),
                (
                    "account",
                    models.CharField(
                        max_length=10,
                        verbose_name="account",
                    ),
                ),
                (
                    "amount",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="amount",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("get", "get"), ("add", "add")],
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("success", "success"),
                            ("timeout", "timeout"),
                            ("unknown_number", "unknown number"),
                            ("unauthorized", "unauthorized"),
                        ],
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="creator",
                    ),
                ),
            ],
            options={
                "verbose_name": "printing quota log",
                "verbose_name_plural": "printing quota logs",
                "ordering": ["-time"],
            },
        ),
    ]
