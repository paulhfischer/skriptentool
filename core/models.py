import os
from datetime import datetime
from math import copysign

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import localtime

from SkriptenTool.storage import OverwriteStorage


def get_product(ean):
    ean = str(ean)
    if LectureNote.objects.filter(ean=ean).exists():
        return LectureNote.objects.get(ean=ean)
    if PrintingQuota.objects.filter(ean=ean).exists():
        return PrintingQuota.objects.get(ean=ean)
    if Deposit.objects.filter(ean=ean).exists():
        return Deposit.objects.get(ean=ean)


def get_type(ean):
    if LectureNote.objects.filter(ean=ean).exists():
        return "lecturenote"
    if PrintingQuota.objects.filter(ean=ean).exists():
        return "printingquota"
    if Deposit.objects.filter(ean=ean).exists():
        return "deposit"


def get_filename(instance, filename):
    filename = instance.ean + ".pdf"
    return os.path.join("media/skripten", filename)


# Kassenvorgänge
class CashBookEntry(models.Model):
    def __str__(self):
        return localtime(self.time).strftime("%d.%m.%Y %H:%M")

    class Meta:
        verbose_name = "Kassenbucheintrag"
        verbose_name_plural = "Kassenbucheinträge"

    @classmethod
    def correction(cls, user, amount):
        cls(user=user, detail="Korrektur", amount=amount).save()

    @classmethod
    def withdrawal(cls, user, amount):
        cls(user=user, detail="Entnahme", amount=amount).save()

    @classmethod
    def deposit(cls, user, amount):
        cls(user=user, detail="Einlage", amount=amount).save()

    @classmethod
    def sale(cls, user, ean, amount):
        cls(user=user, detail="Artikel-EAN: " + ean, amount=amount).save()

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Benutzer")
    time = models.DateTimeField(default=datetime.now, verbose_name="Zeitpunkt")
    detail = models.CharField(max_length=20, verbose_name="Details")
    amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Betrag")


# Kassenstand
class Balance(models.Model):
    def __str__(self):
        return localtime(self.time).strftime("%d.%m.%Y %H:%M")

    class Meta:
        verbose_name = "Kassenstand"
        verbose_name_plural = "Kassenstände"

    @classmethod
    def count_latest(cls, user, amount):
        latest = Balance.objects.latest("time")
        if latest.amount == amount:
            latest.counted = True
            latest.save()
            Balance.objects.filter(type="Zwischenstand").exclude(pk=latest.pk).delete()
        else:
            CashBookEntry.correction(user, amount - latest.amount)
            latest.counted = True
            latest.amount = amount
            latest.save()
            Balance.objects.filter(type="Zwischenstand").exclude(pk=latest.pk).delete()

    @classmethod
    def add_temp(cls, user, amount, counted):
        cls(user=user, amount=amount, counted=counted, type="Zwischenstand").save()

    @classmethod
    def add_update(cls, user, amount):
        Balance.objects.filter(type="Zwischenstand").delete()
        cls(user=user, amount=amount, counted=True, type="Zwischenstand").save()

    @classmethod
    def add_opening(cls, user):
        cls(user=user, amount=Balance.objects.latest("time").amount, counted=False, type="Kassenbeginn").save()

    @classmethod
    def add_closing(cls, user, amount):
        cls(user=user, amount=amount, counted=True, type="Kassenschluss").save()
        Balance.objects.filter(type="Zwischenstand").delete()

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Benutzer")
    time = models.DateTimeField(default=datetime.now, verbose_name="Zeitpunkt")
    amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kassenstand")
    counted = models.BooleanField(verbose_name="Gezählt")
    type = models.CharField(max_length=20, verbose_name="Art")

    def is_opening(self):
        return self.type == "Kassenbeginn"


# Autoren
class Author(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"

    name = models.CharField(max_length=256, verbose_name="Name")
    mail = models.EmailField(max_length=256, verbose_name="E-Mail Adresse")


# Kaution
class Deposit(models.Model):
    def __str__(self):
        return self.name + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Kaution"
        verbose_name_plural = "Kautionen"

    ean = models.CharField(max_length=20, verbose_name="EAN")
    name = models.CharField(max_length=256, verbose_name="Bezeichnung")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Kautionsbetrag")
    active = True


# Skripten
class LectureNote(models.Model):
    def __str__(self):
        return self.name + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Skript"
        verbose_name_plural = "Skripten"

    SUBJECTS = [("M", "Mathematik"), ("P", "Physik"), ("I", "Informatik"), ]
    COLORS = [("F1", "Farbe 1"), ("F2", "Farbe 2"), ]
    PAPERSIZES = [("A4_portrait", "A4 (Hochformat)"), ("A4_landscape", "A4 (Querformat)"), ]
    SIDES = [("simplex", "Einseitig"), ("duplex", "Doppelseitig"), ]
    SEMESTERS = [("S" + str(year), "Sommersemester " + str(year)) for year in range(2015, datetime.now().year)] + [
        ("W" + str(year), "Wintersemester " + str(year) + " / " + str(year + 1)) for year in
        range(2015, datetime.now().year)]

    @classmethod
    def get_subject(cls, subject):
        try:
            return list(filter(lambda x: x[0] == subject, LectureNote.SUBJECTS))[0][1]
        except IndexError:
            return ""

    @classmethod
    def get_color(cls, color):
        try:
            return list(filter(lambda x: x[0] == color, LectureNote.COLORS))[0][1]
        except IndexError:
            return ""

    @classmethod
    def get_papersize(cls, papersize):
        try:
            return list(filter(lambda x: x[0] == papersize, LectureNote.PAPERSIZES))[0][1]
        except IndexError:
            return ""

    @classmethod
    def get_sides(cls, sides):
        try:
            return list(filter(lambda x: x[0] == sides, LectureNote.SIDES))[0][1]
        except IndexError:
            return ""

    @classmethod
    def get_semester(cls, semester):
        try:
            return list(filter(lambda x: x[0] == semester, LectureNote.SEMESTERS))[0][1]
        except IndexError:
            return ""

    ean = models.CharField(max_length=20, verbose_name="EAN")
    name = models.CharField(max_length=256, verbose_name="Skriptname")
    subject = models.CharField(max_length=1, choices=SUBJECTS, null=True, verbose_name="Studiengang")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis")
    study_grants = models.BooleanField(verbose_name="Studienzuschüsse")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, verbose_name="Autor")
    semester_start = models.CharField(max_length=256, choices=SEMESTERS, verbose_name="Semester (von)")
    semester_end = models.CharField(max_length=256, choices=SEMESTERS, null=True, blank=True,
                                    verbose_name="Semester (bis)")
    active = models.BooleanField(verbose_name="Steht zum Verkauf")
    deposit = models.ForeignKey(Deposit, on_delete=models.PROTECT, blank=True, null=True,
                                verbose_name="Kaution")
    stock = models.IntegerField(verbose_name="Bestand", default=0)
    color = models.CharField(max_length=20, choices=COLORS, null=True, blank=True,
                             verbose_name="Deckblattfarbe")
    papersize = models.CharField(max_length=20, choices=PAPERSIZES, null=True, blank=True,
                                 verbose_name="Papiergröße")
    sides = models.CharField(max_length=20, choices=SIDES, null=True, blank=True, verbose_name="Seitigkeit")
    printnotes = models.CharField(max_length=256, verbose_name="Kommentar für Druck", null=True, blank=True)
    file = models.FileField(upload_to=get_filename, verbose_name="Datei", storage=OverwriteStorage(),
                            validators=[FileExtensionValidator(allowed_extensions=["pdf"])])

    def get_deposit(self):
        return self.deposit


# Druckkontingent
class PrintingQuota(models.Model):
    def __str__(self):
        return str(self.pages) + " Seiten" + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Druckkontingent"
        verbose_name_plural = "Druckkontingente"

    def name(self):
        return str(self.pages) + " Seiten"

    ean = models.CharField(max_length=20, verbose_name="EAN")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis")
    pages = models.IntegerField(verbose_name="Seitenzahl")
    active = models.BooleanField(verbose_name="Steht zum Verkauf")


# Verkaufsschichten
class Shift(models.Model):
    def __str__(self):
        if self.time_end:
            return localtime(self.time_start).strftime("%d.%m.%Y") + " (" + localtime(self.time_start).strftime(
                "%H:%M") + " bis " + localtime(self.time_end).strftime("%H:%M") + ")"
        else:
            return localtime(self.time_start).strftime("%d.%m.%Y") + " (" + localtime(self.time_start).strftime(
                "%H:%M") + " bis jetzt)"

    class Meta:
        verbose_name = "Verkaufsschicht"
        verbose_name_plural = "Verkaufsschichten"

    @classmethod
    def end_shift(cls, user):
        if Shift.objects.filter(vendor=user).exists():
            shift = Shift.objects.filter(vendor=user).latest("time_start")
            shift.time_end = datetime.now()
            shift.save()

    time_start = models.DateTimeField(verbose_name="Verkaufsstart")
    time_end = models.DateTimeField(blank=True, null=True, verbose_name="Verkaufsende")
    vendor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Verkäufer")
    valid = models.BooleanField(verbose_name="Überprüft")
    payout = models.BooleanField(verbose_name="Bezahlt")


# Kautionsschein
class DepositNote(models.Model):
    def __str__(self):
        return self.ean

    class Meta:
        verbose_name = "Kautionsschein"
        verbose_name_plural = "Kautionsscheine"

    @classmethod
    def exists(cls, ean):
        return DepositNote.objects.filter(ean=ean).exists()

    @classmethod
    def refunded(cls, ean):
        if DepositNote.exists(ean):
            if DepositNote.objects.get(ean=ean).refunded_time:
                return True
        return False

    @classmethod
    def is_refundable(cls, ean):
        if DepositNote.exists(ean):
            return DepositNote.objects.get(ean=ean).refundable
        return False

    @classmethod
    def refund(cls, ean, user):
        if DepositNote.exists(ean):
            note = DepositNote.objects.get(ean=ean)
            note.refunded_by = user
            note.refunded_time = datetime.now()
            note.save()

    @classmethod
    def new_ean(cls):
        try:
            return str(int(DepositNote.objects.latest("ean").ean) + 1)
        except ObjectDoesNotExist:
            return str(1500)

    ean = models.CharField(max_length=20, verbose_name="EAN")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Kautionsbetrag")
    sold_time = models.DateTimeField(blank=True, null=True, verbose_name="Verkaufszeitpunkt")
    sold_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="sold_by",
                                verbose_name="Verkauft von")
    refunded_time = models.DateTimeField(blank=True, null=True, verbose_name="Rückgabezeitpunkt")
    refunded_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True,
                                    related_name="refunded_by", verbose_name="Zurückgegeben von")
    refundable = models.BooleanField(verbose_name="Darf erstattet werden")

    def is_refunded(self):
        return self.refunded_by


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
        for cart_item in CartItem.objects.filter(cart=self):
            for i in range(abs(cart_item.quantity)):
                CashBookEntry().sale(self.vendor, cart_item.ean, copysign(cart_item.price_single(), cart_item.quantity))

        if str(reason) == "sale" and self.total() != 0:
            Balance().add_temp(self.vendor, Balance.objects.latest("time").amount + self.total(), False)
        elif str(reason) == "closing":
            Balance().add_closing(self.vendor, Balance.objects.latest("time").amount + self.total())
            Shift.end_shift(self.vendor)

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
                    try:
                        product.stock -= 1
                        product.save()
                    except AttributeError:
                        pass
                except ObjectDoesNotExist:
                    cart_item = CartItem(ean=ean, quantity=1, type=get_type(ean), cart=self)
                    cart_item.save()
                    try:
                        product.stock -= 1
                        product.save()
                    except AttributeError:
                        pass

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
                try:
                    product.stock += 1
                    product.save()
                except AttributeError:
                    pass
            except ObjectDoesNotExist:
                cart_item = CartItem(ean=ean, quantity=-1, type=get_type(ean), cart=self)
                cart_item.save()
                try:
                    product.stock += 1
                    product.save()
                except AttributeError:
                    pass

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
        return self.ean

    class Meta:
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"

    TYPES = [("lecturenote", "Skript"), ("printingquota", "Druckkontingent"), ("deposit", "Kautionsschein")]

    ean = models.CharField(max_length=20, verbose_name="EAN")
    type = models.CharField(max_length=256, choices=TYPES, null=True, verbose_name="Art")
    quantity = models.IntegerField(verbose_name="Anzahl")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def price_single(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).price
        elif self.type == "printingquota":
            return PrintingQuota.objects.get(ean=self.ean).price
        elif self.type == "deposit":
            return Deposit.objects.get(ean=self.ean).price

    def name(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).name
        elif self.type == "printingquota":
            return PrintingQuota.objects.get(ean=self.ean).name()
        elif self.type == "deposit":
            return Deposit.objects.get(ean=self.ean).name

    def price_total(self):
        if self.type == "lecturenote":
            return LectureNote.objects.get(ean=self.ean).price * self.quantity
        elif self.type == "printingquota":
            return PrintingQuota.objects.get(ean=self.ean).price * self.quantity
        elif self.type == "deposit":
            return Deposit.objects.get(ean=self.ean).price * self.quantity

    def type_str(self):
        return dict(self.TYPES)[self.type]
