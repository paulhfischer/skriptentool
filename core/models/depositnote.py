from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import User


class DepositNote(models.Model):
    class Meta:
        verbose_name = _("deposit note")
        verbose_name_plural = _("deposit notes")
        ordering = ["number"]

    number = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("number"),
    )

    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("deposit (in €)"),
    )

    sold_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("time of sale"),
    )

    sold_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="sold_by",
        verbose_name=_("sold by"),
    )

    refunded_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("return time"),
    )

    refunded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="refunded_by",
        verbose_name=_("refunded by"),
    )

    refundable = models.BooleanField(
        default=False,
        verbose_name=_("refundable"),
    )

    def __str__(self):
        return str(self.number)

    @property
    def is_refunded(self):
        return self.refunded_by

    @classmethod
    def exists(cls, number):
        return DepositNote.objects.filter(number=number).exists()

    @classmethod
    def refunded(cls, number):
        return DepositNote.exists(number) and DepositNote.objects.get(number=number).refunded_time

    @classmethod
    def is_refundable(cls, number):
        if DepositNote.exists(number):
            return DepositNote.objects.get(number=number).refundable
        return False

    @classmethod
    def refund(cls, number, user):
        if DepositNote.exists(number):
            note = DepositNote.objects.get(number=number)
            note.refunded_by = user
            note.refunded_time = timezone.now()
            note.save()

    @classmethod
    def new_number(cls):
        try:
            return str(int(DepositNote.objects.latest("number").number) + 1)
        except ObjectDoesNotExist:
            return str(1500)

    permissions = {
        "list": {
            "is_referent": "__all__",
        },
        "create": {
            "is_referent": "__all__",
        },
        "update": {
            "is_referent": ["sold_by", "refunded_by", "refundable"],
        },
        "delete": [
            "is_referent",
        ],
    }
