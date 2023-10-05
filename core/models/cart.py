from math import copysign

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from core.models import Balance
from core.models import CashBookEntry
from core.models import get_product
from core.models import get_type
from core.models import Shift
from core.models import User


class Cart(models.Model):
    class Meta:
        verbose_name = _("cart")
        verbose_name_plural = _("carts")
        ordering = ["vendor"]

    CLOSING = "closing"
    SALE = "sale"
    INVOICE = "invoice"

    MI = "MI"
    CH = "CH"
    
    LOCATIONS = [
        (MI, _("MI")),
        (CH, _("CH")),
    ]

    vendor = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("vendor"),
    )

    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("time of creation"),
    )
    
    location = models.CharField(
        max_length=20,
        choices=LOCATIONS,
        default=MI,
        verbose_name=_("location"),
    )

    def __str__(self):
        return str(self.vendor)

    def clean(self):
        # verify that only one cart can be created
        if self.objects.filter(location=self.vendor.default_location).count() > 0 and self.pk != self.objects.filter(location=self.vendor.default_location).get().pk:
            raise ValidationError(_("There can only be one sale at a time."))

    def close(self, reason=CLOSING):
        # add sale entry to cashbook for every item in cart
        if reason == self.INVOICE:
            for cart_item in CartItem.objects.filter(cart=self, location=self.vendor.default_location):
                for _i in range(abs(cart_item.quantity)):
                    CashBookEntry.sale(
                        self.vendor,
                        cart_item.ean,
                        0,
                        self.vendor.default_location,
                    )        
        else:
            for cart_item in CartItem.objects.filter(cart=self, location=self.vendor.default_location):
                for _i in range(abs(cart_item.quantity)):
                    CashBookEntry.sale(
                        self.vendor,
                        cart_item.ean,
                        copysign(cart_item.price_single, cart_item.quantity),
                        self.vendor.default_location,
                    )

        # add cashbookentry and end shift if cart is closed
        if reason == self.SALE and self.total != 0:
            Balance.add_temp(self.vendor, Balance.objects.filter(location=self.vendor.default_location).latest("time").amount + self.total, False, self.vendor.default_location)
        elif reason == self.INVOICE and self.total != 0:
            Balance.add_temp(self.vendor, Balance.objects.filter(location=self.vendor.default_location).latest("time").amount, False, self.vendor.default_location)
        elif reason == self.CLOSING:
            Balance.add_closing(self.vendor, Balance.objects.filter(location=self.vendor.default_location).latest("time").amount + self.total, self.vendor.default_location)
            Shift.end_shift(self.vendor, self.vendor.default_location)

        # remove cart
        self.delete()

    def add(self, ean):
        product = get_product(ean)
        if product.active:
            # increase quanity of cartitem if already exists, create new otherwise
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self, location=self.vendor.default_location)

                # delete item if quantity would be '0'
                if cart_item.quantity == -1:
                    cart_item.delete()
                else:
                    cart_item.quantity += 1
                    cart_item.save()

                # update stock if attribute exists
                try:
                    if self.vendor.default_location == "MI":
                        product.stock_MI -= 1
                        product.save()
                    if self.vendor.default_location == "CH":
                        product.stock_CH -= 1
                        product.save()                        
                except AttributeError:
                    pass
            except ObjectDoesNotExist:
                CartItem(ean=ean, quantity=1, type=get_type(ean), cart=self, location=self.vendor.default_location).save()

                # update stock if attribute exists
                try:
                    if self.vendor.default_location == "MI":
                        product.stock_MI -= 1
                        product.save()
                    if self.vendor.default_location == "CH":
                        product.stock_CH -= 1
                        product.save()         
                except AttributeError:
                    pass

    def remove(self, ean):
        product = get_product(ean)
        if product.active:
            # decrease quanity of cartitem if already exists, create new otherwise
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self, location=self.vendor.default_location)

                # delete item if quantity would be '0'
                if cart_item.quantity == 1:
                    cart_item.delete()
                else:
                    cart_item.quantity -= 1
                    cart_item.save()

                # update stock if attribute exists
                try:
                    if self.vendor.default_location == "MI":
                        product.stock_MI += 1
                        product.save()
                    if self.vendor.default_location == "CH":
                        product.stock_CH += 1
                        product.save()         
                except AttributeError:
                    pass
            except ObjectDoesNotExist:
                CartItem(ean=ean, quantity=-1, type=get_type(ean), cart=self, location=self.vendor.default_location).save()

                # update stock if attribute exists
                try:
                    if self.vendor.default_location == "MI":
                        product.stock_MI += 1
                        product.save()
                    if self.vendor.default_location == "CH":
                        product.stock_CH += 1
                        product.save()  
                except AttributeError:
                    pass

    @property
    def is_empty(self):
        return not CartItem.objects.filter(cart=self, location=self.vendor.default_location).exists()

    @property
    def total(self):
        # count total balance of cart (sum up price of all cart items)
        total = 0
        if not self.is_empty:
            cart_items = CartItem.objects.filter(cart=self, location=self.vendor.default_location)
            for item in cart_items:
                total += item.price_total
        return total


class CartItem(models.Model):
    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")
        ordering = ["cart", "ean"]
        constraints = [models.UniqueConstraint(fields=["ean", "cart"], name="unique_cart_item")]

    LECTURENOTE = "lecturenote"
    PRINTINGQUOTA = "printingquota"
    DEPOSIT = "deposit"
    LABCOAT = "labcoat"

    TYPES = [
        (LECTURENOTE, _("lecture note")),
        (PRINTINGQUOTA, _("printing quota")),
        (DEPOSIT, pgettext_lazy("security deposit", "deposit")),
        (LABCOAT, _("labcoat")),
    ]
    
    MI = "MI"
    CH = "CH"
    
    LOCATIONS = [
        (MI, _("MI")),
        (CH, _("CH")),
    ]

    ean = models.CharField(
        max_length=20,
        verbose_name=_("EAN"),
    )

    type = models.CharField(
        max_length=20,
        choices=TYPES,
        verbose_name=_("type"),
    )

    quantity = models.IntegerField(
        verbose_name=_("quantity"),
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name=_("cart"),
    )
    
    location = models.CharField(
        max_length=20,
        choices=LOCATIONS,
        default=MI,
        verbose_name=_("location"),
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
