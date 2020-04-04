from django.db import models


class Author(models.Model):
    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"
        ordering = ["name"]

    name = models.CharField(
        max_length=256,
        verbose_name="Name",
    )

    mail = models.EmailField(
        max_length=256,
        verbose_name="E-Mail Adresse",
    )

    def __str__(self):
        return self.name

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
