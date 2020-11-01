from django.db import models
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from core.models import User


class PrintingQuotaLog(models.Model):
    class Meta:
        verbose_name = _("printing quota log")
        verbose_name_plural = _("printing quota logs")
        ordering = ["-time"]

    PENDING = "pending"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    UNKNOWN_NUMBER = "unknown_number"
    UNAUTHORIZED = "unauthorized"

    STATUSES = [
        (PENDING, _("pending")),
        (SUCCESS, _("success")),
        (TIMEOUT, _("timeout")),
        (UNKNOWN_NUMBER, _("unknown number")),
        (UNAUTHORIZED, _("unauthorized")),
    ]

    GET = "get"
    ADD = "add"

    TYPES = [
        (GET, _("get")),
        (ADD, _("add")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("creator"),
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("time"),
    )

    account = models.CharField(
        max_length=10,
        verbose_name=_("account"),
    )

    amount = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("amount"),
    )

    type = models.CharField(
        max_length=20,
        choices=TYPES,
        verbose_name=_("type"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        verbose_name=_("status"),
    )

    def __str__(self):
        return date_format(timezone.localtime(self.time), "SHORT_DATETIME_FORMAT")
