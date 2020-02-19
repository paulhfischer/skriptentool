from datetime import datetime
from math import copysign

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


# Funktionen
def get_product(ean):
    if LectureNote.objects.filter(ean=ean).exists():
        return LectureNote.objects.get(ean=ean)


def get_type(ean):
    if LectureNote.objects.filter(ean=ean).exists():
        return "lecturenote"


# Abgeschlossene Verkäufe
class Sale(models.Model):
    def __str__(self):
        return self.time.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Verkauf"
        verbose_name_plural = "Verkäufe"

    vendor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Verkäufer")
    time = models.DateTimeField(default=datetime.now, verbose_name="Verkaufszeitpunkt")
    ean = models.IntegerField(verbose_name="EAN")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis")


# Kassenstand
class Account(models.Model):
    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Kassenstand"
        verbose_name_plural = "Kassenstände"

    TYPE = [
        ("withdrawal", "Abschöpfen"),
        ("sale", "Verkauf"),
        ("opening", "Kassenöfnung"),
        ("closing", "Kassenschluss"),
        ("correction", "Korrektur"),
    ]

    date = models.DateTimeField(default=datetime.now, verbose_name="Zeitpunkt")
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Nutzer")
    balance = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kassenstand")
    counted = models.BooleanField(default=False, verbose_name="Gezählt")
    type = models.CharField(max_length=20, choices=TYPE, null=True, verbose_name="Art")


# Autoren
class Author(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"

    name = models.CharField(max_length=256, verbose_name="Name")
    mail = models.EmailField(max_length=256, verbose_name="E-Mail Adresse")


# Skripten
class LectureNote(models.Model):
    def __str__(self):
        return self.name + " (" + str(self.ean) + ")"

    class Meta:
        verbose_name = "Skript"
        verbose_name_plural = "Skripten"

    SUBJECTS = [
        ("M", "Mathematik"),
        ("P", "Physik"),
        ("I", "Informatik"),
    ]
    COLORS = [
        ("F1", "Farbe 1"),
        ("F2", "Farbe 2"),
    ]
    PAPERSIZES = [
        ("A4_portrait", "A4 (Hochformat)"),
        ("A4_landscape", "A4 (Querformat)"),
    ]
    SIDES = [
        ("simplex", "Einseitig"),
        ("duplex", "Doppelseitig"),
    ]
    SEMESTERS = [("S" + str(year), "Sommersemester " + str(year)) for year in range(2015, datetime.now().year)] + [
        ("W" + str(year), "Wintersemester " + str(year) + " / " + str(year + 1)) for year in
        range(2015, datetime.now().year)]

    ean = models.IntegerField(verbose_name="EAN")
    name = models.CharField(max_length=256, verbose_name="Skriptname")
    subject = models.CharField(max_length=1, choices=SUBJECTS, null=True, verbose_name="Studiengang")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, verbose_name="Autor")
    semester_start = models.CharField(max_length=256, choices=SEMESTERS, null=True, verbose_name="Semester (von)")
    semester_end = models.CharField(max_length=256, choices=SEMESTERS, null=True, verbose_name="Semester (bis)")
    active = models.BooleanField(verbose_name="Steht zum Verkauf")
    stock = models.IntegerField(verbose_name="Bestand")
    color = models.CharField(max_length=20, choices=COLORS, null=True, verbose_name="Deckblattfarbe")
    papersize = models.CharField(max_length=20, choices=PAPERSIZES, null=True, verbose_name="Papiergröße")
    sides = models.CharField(max_length=20, choices=SIDES, null=True, verbose_name="Seitigkeit")
    printnotes = models.CharField(max_length=256, verbose_name="Kommentar für Druck")
    file = models.FileField(upload_to="archiv/", verbose_name="Datei")


# Verkaufsvorgänge
class Cart(models.Model):
    def __str__(self):
        return str(self.vendor)

    class Meta:
        verbose_name = "Verkaufsvorgang"
        verbose_name_plural = "Verkaufsvorgänge"

    vendor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Verkäufer")
    time = models.DateTimeField(default=datetime.now, verbose_name="Erstellzeitpunkt")

    def is_empty(self):
        return not CartItem.objects.filter(cart=self).exists()

    def close(self, reason):
        sale_time = datetime.now()
        for cart_item in CartItem.objects.filter(cart=self):
            for i in range(abs(cart_item.quantity)):
                sale = Sale(vendor=self.vendor, time=sale_time, ean=cart_item.ean,
                            price=copysign(cart_item.price_single(), cart_item.quantity))
                sale.save()

        if str(reason) == "sale" and self.total() != 0:
            Account(changed_by=self.vendor, balance=Account.objects.latest("date").balance + self.total(),
                    counted=False, type=str(reason)).save()
        elif str(reason) == "opening" or str(reason) == "closing":
            Account(changed_by=self.vendor, balance=Account.objects.latest("date").balance + self.total(),
                    counted=True, type=str(reason)).save()
            Account.objects.filter(type="sale").delete()

        self.delete()

    def add(self, ean):
        product = get_product(ean)
        if product:
            if product.active:
                try:
                    cart_item = CartItem.objects.get(ean=ean, cart=self)
                    if cart_item.quantity == -1:
                        cart_item.delete()
                    else:
                        cart_item.quantity += 1
                        cart_item.save()
                    product.stock -= 1
                    product.save()
                except ObjectDoesNotExist:
                    cart_item = CartItem(ean=ean, quantity=1, type=get_type(ean), cart=self)
                    cart_item.save()
                    product.stock -= 1
                    product.save()

    def remove(self, ean):
        product = get_product(ean)
        if product:
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self)
                if cart_item.quantity == 1:
                    cart_item.delete()
                else:
                    cart_item.quantity -= 1
                    cart_item.save()
                product.stock += 1
                product.save()
            except ObjectDoesNotExist:
                cart_item = CartItem(ean=ean, quantity=-1, type=get_type(ean), cart=self)
                cart_item.save()
                product.stock += 1
                product.save()

    def total(self):
        total = 0
        try:
            cart_items = CartItem.objects.filter(cart=self)
            for item in cart_items:
                total += item.price_total()
        except ObjectDoesNotExist:
            pass
        return total


# Artikel in Verkaufsvorgängen
class CartItem(models.Model):
    def __str__(self):
        return str(self.ean)

    class Meta:
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"

    TYPES = [
        ("lecturenote", "Skript"),
        ("quota", "Druckkontingent"),
        ("deposit", "Kautionsschein"),
    ]

    ean = models.IntegerField(verbose_name="EAN")
    type = models.CharField(max_length=256, choices=TYPES, null=True, verbose_name="Art")
    quantity = models.IntegerField(verbose_name="Anzahl")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def price_single(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).price
        elif self.type == "quota":
            return LectureNote.objects.get(ean=self.ean).price
        elif self.type == "deposit":
            return LectureNote.objects.get(ean=self.ean).price

    def name(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).name
        elif self.type == "quota":
            return LectureNote.objects.get(ean=self.ean).name
        elif self.type == "deposit":
            return LectureNote.objects.get(ean=self.ean).name

    def price_total(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).price * self.quantity
        elif self.type == "quota":
            return LectureNote.objects.get(ean=self.ean).price * self.quantity
        elif self.type == "deposit":
            return LectureNote.objects.get(ean=self.ean).price * self.quantity

    def type_str(self):
        return dict(self.TYPES)[self.type]
