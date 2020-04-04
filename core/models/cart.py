from math import copysign

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import Balance
from core.models import CashBookEntry
from core.models import get_product
from core.models import get_type
from core.models import Shift
from core.models import User


class Cart(models.Model):
    class Meta:
        verbose_name = "Verkaufsvorgang"
        verbose_name_plural = "Verkaufsvorgänge"
        ordering = ["vendor"]

    vendor = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name="Verkäufer",
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Erstellzeitpunkt",
    )

    def __str__(self):
        return str(self.vendor)

    def clean(self):
        # verify that only one cart can be created
        if self.objects.count() > 0 and self.pk != self.objects.get().pk:
            raise ValidationError("Es darf nur ein Verkauf gleichzeitig stattfinden.")

    def close(self, reason="closing"):
        # add sale entry to cashbook for every item in cart
        for cart_item in CartItem.objects.filter(cart=self):
            for _ in range(abs(cart_item.quantity)):
                CashBookEntry.sale(
                    self.vendor,
                    cart_item.ean,
                    copysign(cart_item.price_single, cart_item.quantity),
                )

        # add cashbookentry and end shift if cart is closed
        if reason == "sale" and self.total != 0:
            Balance.add_temp(self.vendor, Balance.objects.latest("time").amount + self.total, False)
        elif reason == "closing":
            Balance.add_closing(self.vendor, Balance.objects.latest("time").amount + self.total)
            Shift.end_shift(self.vendor)

        # remove cart
        self.delete()

    def add(self, ean):
        product = get_product(ean)
        if product.active:
            # increase quanity of cartitem if already exists, create new otherwise
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self)

                # delete item if quantity would be '0'
                if cart_item.quantity == -1:
                    cart_item.delete()
                else:
                    cart_item.quantity += 1
                    cart_item.save()

                # update stock if attribute exists
                try:
                    product.stock -= 1
                    product.save()
                except AttributeError:
                    pass
            except ObjectDoesNotExist:
                CartItem(ean=ean, quantity=1, type=get_type(ean), cart=self).save()

                # update stock if attribute exists
                try:
                    product.stock -= 1
                    product.save()
                except AttributeError:
                    pass

    def remove(self, ean):
        product = get_product(ean)
        if product.active:
            # decrease quanity of cartitem if already exists, create new otherwise
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self)

                # delete item if quantity would be '0'
                if cart_item.quantity == 1:
                    cart_item.delete()
                else:
                    cart_item.quantity -= 1
                    cart_item.save()

                # update stock if attribute exists
                try:
                    product.stock += 1
                    product.save()
                except AttributeError:
                    pass
            except ObjectDoesNotExist:
                CartItem(ean=ean, quantity=-1, type=get_type(ean), cart=self).save()

                # update stock if attribute exists
                try:
                    product.stock += 1
                    product.save()
                except AttributeError:
                    pass

    @property
    def is_empty(self):
        return not CartItem.objects.filter(cart=self).exists()

    @property
    def total(self):
        # count total balance of cart (sum up price of all cart items)
        total = 0
        if not self.is_empty:
            cart_items = CartItem.objects.filter(cart=self)
            for item in cart_items:
                total += item.price_total
        return total


class CartItem(models.Model):
    class Meta:
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"
        ordering = ["cart", "ean"]
        constraints = [models.UniqueConstraint(fields=["ean", "cart"], name="unique_cart_item")]

    TYPES = [
        ("lecturenote", "Skript"),
        ("printingquota", "Druckkontingent"),
        ("deposit", "Kautionsschein"),
    ]

    ean = models.CharField(
        max_length=20,
        verbose_name="EAN",
    )

    type = models.CharField(
        max_length=20,
        choices=TYPES,
        verbose_name="Art",
    )

    quantity = models.IntegerField(
        verbose_name="Anzahl",
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name="Verkaufsvorgang",
    )

    def __str__(self):
        return self.ean

    @property
    def price_single(self):
        return get_product(self.ean).price

    @property
    def price_total(self):
        return self.price_single * self.quantity

    @property
    def name(self):
        return get_product(self.ean).name
