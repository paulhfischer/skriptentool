from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation
from django.utils.formats import date_format
from django.utils.text import capfirst
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from core.models import CashBookEntry
from core.models import User
from skriptentool import config
from skriptentool import settings


class Balance(models.Model):
    class Meta:
        verbose_name = _("balance")
        verbose_name_plural = _("balances")
        ordering = ["-time"]

    TYPES = [
        ("initial", _("initial")),
        ("opening", _("opening")),
        ("closing", _("closing")),
        ("temporary", _("temporary")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("user"),
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("time"),
    )

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("amount (in €)"),
    )

    counted = models.BooleanField(
        default=False,
        verbose_name=_("counted"),
    )

    type = models.CharField(
        max_length=20,
        choices=TYPES,
        verbose_name=_("type"),
    )

    def __str__(self):
        return date_format(timezone.localtime(self.time), "SHORT_DATETIME_FORMAT")

    @property
    def is_opening(self):
        return self.type == "opening"

    @classmethod
    def count_latest(cls, user, amount):
        # set counted of the latest model instance to true if counted amount is correct, add
        # correction otherwise
        latest = Balance.objects.latest("time")
        if latest.amount == amount:
            latest.counted = True
            latest.save()

            # remove all temporary balances
            Balance.objects.filter(type="temporary").exclude(pk=latest.pk).delete()
        else:
            CashBookEntry.correction(user, amount - latest.amount)

            latest.counted = True
            latest.amount = amount
            latest.save()

            # remove all temporary balances
            Balance.objects.filter(type="temporary").exclude(pk=latest.pk).delete()

    @classmethod
    def add_temp(cls, user, amount, counted):
        Balance(user=user, amount=amount, counted=counted, type="temporary").save()

    @classmethod
    def add_update(cls, user, amount):
        Balance.objects.filter(type="temporary").delete()
        Balance(user=user, amount=amount, counted=True, type="temporary").save()

    @classmethod
    def add_opening(cls, user):
        Balance(
            user=user,
            amount=Balance.objects.latest("time").amount,
            counted=False,
            type="opening",
        ).save()

    @classmethod
    def add_closing(cls, user, amount):
        Balance(user=user, amount=amount, counted=True, type="closing").save()
        Balance.objects.filter(type="temporary").delete()

        # send email if balance is too high
        if amount >= 1000:
            with translation.override(settings.LANGUAGE_CODE):
                send_mail(
                    subject=format_lazy("[Skriptentool] {}", capfirst(_("high balance"))),
                    message=render_to_string("core/mail/high_balance.txt", {"balance": amount}),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=config.FINANCE_EMAILS,
                )
