from django.db import models
from django.utils import timezone

from core.models import User


class CashBookEntry(models.Model):
    class Meta:
        verbose_name = "Kassenbucheintrag"
        verbose_name_plural = "Kassenbucheinträge"
        ordering = ["-time"]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Ersteller",
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Zeitpunkt",
    )

    detail = models.CharField(
        max_length=20,
        verbose_name="Details",
    )

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Betrag in Euro",
    )

    def __str__(self):
        return timezone.localtime(self.time).strftime("%d.%m.%Y %H:%M")

    @classmethod
    def correction(cls, user, amount):
        CashBookEntry(user=user, detail="Korrektur", amount=amount).save()

    @classmethod
    def withdrawal(cls, user, amount):
        CashBookEntry(user=user, detail="Entnahme", amount=amount).save()

    @classmethod
    def deposit(cls, user, amount):
        CashBookEntry(user=user, detail="Einlage", amount=amount).save()

    @classmethod
    def sale(cls, user, ean, amount):
        CashBookEntry(user=user, detail=f"Artikel-EAN: {ean}", amount=amount).save()
