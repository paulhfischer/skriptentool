from django.db import models
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from core.models import User


class Shift(models.Model):
    class Meta:
        verbose_name = _("sales shift")
        verbose_name_plural = _("sales shifts")
        ordering = ["-time_start"]

    time_start = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("start time"),
    )

    time_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("end time"),
    )

    vendor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("vendor"),
    )

    valid = models.BooleanField(
        default=False,
        verbose_name=_("reviewed"),
    )

    payout = models.BooleanField(
        default=False,
        verbose_name=_("beverages"),
    )

    # generate displayname (depending on range or single-semester)
    def __str__(self):
        if self.time_end:
            return str(
                _("%(date)s (%(time_start)s until %(time_end)s)")
                % {
                    "date": date_format(timezone.localtime(self.time_start), "SHORT_DATE_FORMAT"),
                    "time_start": date_format(timezone.localtime(self.time_start), "TIME_FORMAT"),
                    "time_end": date_format(timezone.localtime(self.time_end), "TIME_FORMAT"),
                },
            )

        return str(
            _("%(date)s (%(time_start)s until now)")
            % {
                "date": date_format(timezone.localtime(self.time_start), "SHORT_DATE_FORMAT"),
                "time_start": date_format(timezone.localtime(self.time_start), "TIME_FORMAT"),
            },
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
