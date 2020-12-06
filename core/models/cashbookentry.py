from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation
from django.utils.formats import date_format
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from core.models import User


class CashBookEntry(models.Model):
    class Meta:
        verbose_name = _("cash book entry")
        verbose_name_plural = _("cash book entries")
        ordering = ["-time"]

    CORRECTION = "correction"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    SALE = "sale"

    TYPES = [
        (CORRECTION, _("correction")),
        (WITHDRAWAL, _("withdrawal")),
        (DEPOSIT, _("deposit")),
        (SALE, _("sale")),
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

    type = models.CharField(
        max_length=20,
        choices=TYPES,
        verbose_name=_("type"),
    )

    detail = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_("detail"),
    )

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("amount (in €)"),
    )

    def __str__(self):
        return date_format(timezone.localtime(self.time), "SHORT_DATETIME_FORMAT")

    @property
    def text(self):
        if self.type == self.CORRECTION:
            return _("correction")
        elif self.type == self.WITHDRAWAL:
            return (
                format_lazy("{} ({})", _("withdrawal"), self.detail)
                if self.detail
                else _("withdrawal")
            )
        elif self.type == self.DEPOSIT:
            return (
                format_lazy("{} ({})", _("deposit"), self.detail) if self.detail else _("deposit")
            )
        elif self.type == self.SALE:
            return format_lazy("{}: {}", _("EAN"), self.detail)

        raise TypeError

    @classmethod
    def correction(cls, user, amount):
        CashBookEntry(user=user, type=cls.CORRECTION, amount=amount).save()

        with translation.override(settings.LANGUAGE_CODE):
            send_mail(
                subject=format_lazy("[Skriptentool] {}", _("Correction")),
                message=render_to_string(
                    "core/mail/correction.txt",
                    {"user": user, "amount": amount},
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.FINANCE_EMAILS,
            )

    @classmethod
    def withdrawal(cls, user, amount, comment):
        CashBookEntry(user=user, type=cls.WITHDRAWAL, detail=comment, amount=amount).save()

    @classmethod
    def deposit(cls, user, amount, comment):
        CashBookEntry(user=user, type=cls.DEPOSIT, detail=comment, amount=amount).save()

    @classmethod
    def sale(cls, user, ean, amount):
        CashBookEntry(user=user, type=cls.SALE, detail=ean, amount=amount).save()
