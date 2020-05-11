from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")
        ordering = ["name"]

    name = models.CharField(
        max_length=256,
        verbose_name=_("name"),
    )

    mail = models.EmailField(
        max_length=256,
        verbose_name=_("mail"),
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
