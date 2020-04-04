from django.db import models
from django.utils import timezone

from core.models import User


class Shift(models.Model):
    class Meta:
        verbose_name = "Verkaufsschicht"
        verbose_name_plural = "Verkaufsschichten"
        ordering = ["-time_start"]

    time_start = models.DateTimeField(
        default=timezone.now,
        verbose_name="Verkaufsstart",
    )

    time_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Verkaufsende",
    )

    vendor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Verkäufer",
    )

    valid = models.BooleanField(
        default=False,
        verbose_name="Überprüft",
    )

    payout = models.BooleanField(
        default=False,
        verbose_name="Getränke",
    )

    # generate displayname (depending on range or single-semester)
    def __str__(self):
        if self.time_end:
            return (
                f'{timezone.localtime(self.time_start).strftime("%d.%m.%Y")} '
                f'({timezone.localtime(self.time_start).strftime("%H:%M")} bis '
                f'{timezone.localtime(self.time_end).strftime("%H:%M")})'
            )
        else:
            return (
                f'{timezone.localtime(self.time_start).strftime("%d.%m.%Y")} '
                f'({timezone.localtime(self.time_start).strftime("%H:%M")} bis jetzt)'
            )

    @classmethod
    def end_shift(cls, user):
        shift = Shift.objects.filter(vendor=user).latest("time_start")
        shift.time_end = timezone.now()
        shift.save()

    permissions = {
        "list": {
            "is_referent": "__all__",
            "is_financier": "__all__",
        },
        "create": {
            "is_admin": "__all__",
        },
        "update": {
            "is_referent": ["vendor", "valid"],
            "is_financier": ["payout"],
        },
        "delete": [
            "is_referent",
        ],
    }
