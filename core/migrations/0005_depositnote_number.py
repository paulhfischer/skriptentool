from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_printingquota_log"),
    ]

    operations = [
        migrations.AlterField(
            model_name="depositnote",
            name="number",
            field=models.PositiveIntegerField(
                unique=True,
                verbose_name="number",
            ),
        ),
    ]
