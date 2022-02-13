from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cashbookentry",
            name="detail",
            field=models.CharField(
                max_length=256,
                verbose_name="Details",
            ),
        ),
    ]
