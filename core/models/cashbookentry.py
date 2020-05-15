from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation
from django.utils.formats import date_format
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from core.models import User
from skriptentool import config
from skriptentool import settings


class CashBookEntry(models.Model):
    class Meta:
        verbose_name = _("cash book entry")
        verbose_name_plural = _("cash book entries")
        ordering = ["-time"]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("creator"),
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("time"),
    )

    detail = models.CharField(
        max_length=256,
        verbose_name=_("detail"),
    )

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("amount (in €)"),
    )

    def __str__(self):
        return date_format(timezone.localtime(self.time), "SHORT_DATETIME_FORMAT")

    @classmethod
    def correction(cls, user, amount):
        CashBookEntry(user=user, detail="Korrektur", amount=amount).save()

        with translation.override(settings.LANGUAGE_CODE):
            send_mail(
                subject=format_lazy("[Skriptentool] {}", _("Correction")),
                message=render_to_string(
                    "core/mail/correction.txt",
                    {"user": user, "amount": amount},
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=config.FINANCE_EMAILS,
            )

    @classmethod
    def withdrawal(cls, user, amount, comment):
        if comment:
            CashBookEntry(user=user, detail=f"Entnahme ({comment})", amount=amount).save()
        else:
            CashBookEntry(user=user, detail="Entnahme", amount=amount).save()

    @classmethod
    def deposit(cls, user, amount, comment):
        if comment:
            CashBookEntry(user=user, detail=f"Einlage ({comment})", amount=amount).save()
        else:
            CashBookEntry(user=user, detail="Einlage", amount=amount).save()

    @classmethod
    def sale(cls, user, ean, amount):
        CashBookEntry(user=user, detail=f"Artikel-EAN: {ean}", amount=amount).save()
