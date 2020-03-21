import os
from decimal import Decimal
from math import copysign

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy

from SkriptenTool import settings
from SkriptenTool.storage import OverwriteStorage


# return model instance from ean
# necessary as lecturenotes, printingquota and deposit are different models
def get_product(ean):
    ean = str(ean)
    if LectureNote.objects.filter(ean=ean).exists():
        return LectureNote.objects.get(ean=ean)
    elif PrintingQuota.objects.filter(ean=ean).exists():
        return PrintingQuota.objects.get(ean=ean)
    elif Deposit.objects.filter(ean=ean).exists():
        return Deposit.objects.get(ean=ean)
    else:
        raise ObjectDoesNotExist("Produkt mit der EAN " + ean + " wurde nicht gefunden!")


# return model type from ean
# necessary as lecturenotes, printingquota and deposit are different models
def get_type(ean):
    if LectureNote.objects.filter(ean=ean).exists():
        return "lecturenote"
    elif PrintingQuota.objects.filter(ean=ean).exists():
        return "printingquota"
    elif Deposit.objects.filter(ean=ean).exists():
        return "deposit"
    else:
        raise ObjectDoesNotExist("Produkt mit der EAN " + ean + " wurde nicht gefunden!")


# return path to lecturenote-pdf, relative to media folder
def get_filename(instance, filename):
    return os.path.join(os.path.relpath(settings.LECTURE_NOTES_DIR, settings.MEDIA_ROOT), instance.ean + ".pdf")


# check if input is value for form validation
def validate_number(value):
    if not value.isdigit():
        raise ValidationError(
            gettext_lazy("%(value)s ist keine Zahl"),
            params={"value": value}
        )


# check of input ean already exists for form validation
# necessary as lecturenotes, printingquota and deposit are different models
def validate_unique(obj, model, exclude):
    errors = {}
    try:
        super(model, obj).clean_fields(exclude)
    except ValidationError as e:
        errors.update(e)

    if LectureNote.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists() or \
            PrintingQuota.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists() or \
            Deposit.objects.exclude(pk=obj.pk).filter(ean=obj.ean).exists():
        errors.update({'ean': ["Ein Artikel mit dieser EAN existiert bereits"]})

    if errors:
        raise ValidationError(errors)


class CashBookEntry(models.Model):
    def __str__(self):
        return timezone.localtime(self.time).strftime("%d.%m.%Y %H:%M")

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
    time = models.DateTimeField(default=timezone.now, verbose_name="Zeitpunkt")
    detail = models.CharField(max_length=20, verbose_name="Details")
    amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Betrag in Euro")


class Balance(models.Model):
    def __str__(self):
        return timezone.localtime(self.time).strftime("%d.%m.%Y %H:%M")

    class Meta:
        verbose_name = "Kassenstand"
        verbose_name_plural = "Kassenstände"

    # set counted of latest model instance to true if counted amount is correct, add correction otherwise
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
    time = models.DateTimeField(default=timezone.now, verbose_name="Zeitpunkt")
    amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kassenstand in Euro")
    counted = models.BooleanField(verbose_name="Gezählt")
    type = models.CharField(max_length=20, verbose_name="Art")

    def is_opening(self):
        return self.type == "Kassenbeginn"


class Author(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"

    name = models.CharField(max_length=256, verbose_name="Name")
    mail = models.EmailField(max_length=256, verbose_name="E-Mail Adresse")


class Deposit(models.Model):
    def __str__(self):
        return self.name + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Kaution"
        verbose_name_plural = "Kautionen"

    ean = models.CharField(max_length=20, verbose_name="EAN", validators=[validate_number])
    name = models.CharField(max_length=256, verbose_name="Bezeichnung")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Kautionsbetrag in Euro")
    active = True

    # overwrite validation function to check if ean is unique
    def clean_fields(self, exclude=None):
        validate_unique(self, Deposit, exclude)


class LectureNote(models.Model):
    def __str__(self):
        return self.name + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Skript"
        verbose_name_plural = "Skripten"

    SUBJECTS = [("M", "Mathematik"),
                ("P", "Physik"),
                ("I", "Informatik")]
    COLORS = [("royalblau", "Royalblau"),
              ("eisblau", "Eisblau"),
              ("karibikblau", "Karibikblau"),
              ("seegrün", "Seegrün"),
              ("grasgrün", "Grasgrün"),
              ("maigrün", "Maigrün"),
              ("grau", "Grau"),
              ("fuchsia", "Fuchsia"),
              ("lila", "Lila"),
              ("violett", "Violett"),
              ("ziegelrot", "Ziegelrot"),
              ("rosa", "Rosa"),
              ("lachs", "Lachs"),
              ("orange", "Orange"),
              ("camel", "Camel"),
              ("hellgelb", "Hellgelb"),
              ("goldgelb", "Goldgelb"),
              ("chamois", "Chamois")]
    PAPERSIZES = [("A4_portrait", "A4 (Hochformat)"),
                  ("A4_landscape", "A4 (Querformat)")]
    SIDES = [("simplex", "Einseitig"),
             ("duplex", "Doppelseitig")]
    # semesters have to be updated manually
    SEMESTERS = [("W" + str(year), "Wintersemester " + str(year) + " / " + str(year + 1)) for year in range(2015, 2025)] + \
                [("S" + str(year), "Sommersemester " + str(year)) for year in range(2016, 2025)]

    # return displayname of subject
    @classmethod
    def get_subject(cls, subject):
        try:
            return dict(cls.SUBJECTS)[subject]
        except KeyError:
            return ""

    # return displayname of color
    @classmethod
    def get_color(cls, color):
        try:
            return dict(cls.COLORS)[color]
        except KeyError:
            return ""

    # return displayname of papersize
    @classmethod
    def get_papersize(cls, papersize):
        try:
            return dict(cls.PAPERSIZES)[papersize]
        except KeyError:
            return ""

    # return displayname of sides
    @classmethod
    def get_sides(cls, sides):
        try:
            return dict(cls.SIDES)[sides]
        except KeyError:
            return ""

    # return displayname of semester
    @classmethod
    def get_semester(cls, semester):
        try:
            return dict(cls.SEMESTERS)[semester]
        except KeyError:
            return ""

    ean = models.CharField(max_length=20, verbose_name="EAN", validators=[validate_number])
    name = models.CharField(max_length=256, verbose_name="Skriptname")
    subject = models.CharField(max_length=1, choices=SUBJECTS, null=True, verbose_name="Studiengang")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis", validators=[MinValueValidator(Decimal(0.00))])
    study_grants = models.BooleanField(verbose_name="Studienzuschüsse")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, verbose_name="Autor")
    semester_start = models.CharField(max_length=256, choices=SEMESTERS, verbose_name="Semester (von)")
    semester_end = models.CharField(max_length=256, choices=SEMESTERS, null=True, blank=True, verbose_name="Semester (bis)")
    active = models.BooleanField(verbose_name="Steht zum Verkauf")
    deposit = models.ForeignKey(Deposit, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Kaution")
    stock = models.IntegerField(verbose_name="Bestand", default=0)
    color = models.CharField(max_length=20, choices=COLORS, null=True, blank=True, verbose_name="Deckblattfarbe")
    papersize = models.CharField(max_length=20, choices=PAPERSIZES, null=True, blank=True, verbose_name="Papiergröße")
    sides = models.CharField(max_length=20, choices=SIDES, null=True, blank=True, verbose_name="Seitigkeit")
    printnotes = models.CharField(max_length=256, verbose_name="Kommentar für Druck", null=True, blank=True)
    file = models.FileField(upload_to=get_filename, verbose_name="Datei", storage=OverwriteStorage(), validators=[FileExtensionValidator(allowed_extensions=["pdf"])])

    def get_deposit(self):
        return self.deposit

    # overwrite validation function to check if ean is unique
    def clean_fields(self, exclude=None):
        validate_unique(self, LectureNote, exclude)


class PrintingQuota(models.Model):
    def __str__(self):
        return str(self.pages) + " Seiten" + " (" + self.ean + ")"

    class Meta:
        verbose_name = "Druckkontingent"
        verbose_name_plural = "Druckkontingente"

    def name(self):
        return str(self.pages) + " Seiten"

    ean = models.CharField(max_length=20, verbose_name="EAN", validators=[validate_number])
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis in Euro")
    pages = models.IntegerField(verbose_name="Seitenzahl")
    active = models.BooleanField(verbose_name="Steht zum Verkauf")

    # overwrite validation function to check if ean is unique
    def clean_fields(self, exclude=None):
        validate_unique(self, PrintingQuota, exclude)


class Shift(models.Model):
    # generate displayname (depending on range or single-semester)
    def __str__(self):
        if self.time_end:
            return timezone.localtime(self.time_start).strftime("%d.%m.%Y") \
                   + " (" \
                   + timezone.localtime(self.time_start).strftime("%H:%M") \
                   + " bis " \
                   + timezone.localtime(self.time_end).strftime("%H:%M") \
                   + ")"
        else:
            return timezone.localtime(self.time_start).strftime("%d.%m.%Y") \
                   + " (" \
                   + timezone.localtime(self.time_start).strftime("%H:%M") \
                   + " bis jetzt)"

    class Meta:
        verbose_name = "Verkaufsschicht"
        verbose_name_plural = "Verkaufsschichten"

    @classmethod
    def end_shift(cls, user):
        if Shift.objects.filter(vendor=user).exists():
            shift = Shift.objects.filter(vendor=user).latest("time_start")
            shift.time_end = timezone.now()
            shift.save()

    time_start = models.DateTimeField(verbose_name="Verkaufsstart")
    time_end = models.DateTimeField(blank=True, null=True, verbose_name="Verkaufsende")
    vendor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Verkäufer")
    valid = models.BooleanField(verbose_name="Überprüft")
    payout = models.BooleanField(verbose_name="Bezahlt")


class DepositNote(models.Model):
    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Kautionsschein"
        verbose_name_plural = "Kautionsscheine"

    @classmethod
    def exists(cls, number):
        return DepositNote.objects.filter(number=number).exists()

    @classmethod
    def refunded(cls, number):
        if DepositNote.exists(number):
            if DepositNote.objects.get(number=number).refunded_time:
                return True
        return False

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

    number = models.CharField(max_length=20, verbose_name="Kautionsscheinnummer")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Kautionsbetrag in Euro")
    sold_time = models.DateTimeField(blank=True, null=True, verbose_name="Verkaufszeitpunkt")
    sold_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="sold_by", verbose_name="Verkauft von")
    refunded_time = models.DateTimeField(blank=True, null=True, verbose_name="Rückgabezeitpunkt")
    refunded_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="refunded_by", verbose_name="Zurückgegeben von")
    refundable = models.BooleanField(verbose_name="Erstattbar")

    def is_refunded(self):
        return self.refunded_by


class Cart(models.Model):
    def __str__(self):
        return str(self.vendor)

    class Meta:
        verbose_name = "Verkaufsvorgang"
        verbose_name_plural = "Verkaufsvorgänge"

    vendor = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name="Verkäufer")
    time = models.DateTimeField(default=timezone.now, verbose_name="Erstellzeitpunkt")

    def is_empty(self):
        return not CartItem.objects.filter(cart=self).exists()

    def close(self, reason):
        # add sale entry to cashbook for every item in cart
        for cart_item in CartItem.objects.filter(cart=self):
            for i in range(abs(cart_item.quantity)):
                CashBookEntry().sale(self.vendor, cart_item.ean, copysign(cart_item.price_single(), cart_item.quantity))

        # add entry to cashbook depending on next sale opened or sale closed
        if str(reason) == "sale" and self.total() != 0:
            Balance().add_temp(self.vendor, Balance.objects.latest("time").amount + self.total(), False)
        elif str(reason) == "closing":
            Balance().add_closing(self.vendor, Balance.objects.latest("time").amount + self.total())
            Shift.end_shift(self.vendor)

        # remove cart
        self.delete()

    def add(self, ean):
        product = get_product(ean)
        if product:
            if product.active:
                # increase quanity of cartitem if already exists, create new otherwise
                try:
                    cart_item = CartItem.objects.get(ean=ean, cart=self)
                    # delete item if quantity would be "0"
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
                    cart_item = CartItem(ean=ean, quantity=1, type=get_type(ean), cart=self)
                    cart_item.save()
                    # update stock if attribute exists
                    try:
                        product.stock -= 1
                        product.save()
                    except AttributeError:
                        pass

    def remove(self, ean):
        product = get_product(ean)
        if product:
            # decrease quanity of cartitem if already exists, create new otherwise
            try:
                cart_item = CartItem.objects.get(ean=ean, cart=self)
                # delete item if quantity would be "0"
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
                cart_item = CartItem(ean=ean, quantity=-1, type=get_type(ean), cart=self)
                cart_item.save()
                # update stock if attribute exists
                try:
                    product.stock += 1
                    product.save()
                except AttributeError:
                    pass

    # count total balance of cart (sum up price of all cart items)
    def total(self):
        total = 0
        if not self.is_empty():
            cart_items = CartItem.objects.filter(cart=self)
            for item in cart_items:
                total += item.price_total()
        return total


class CartItem(models.Model):
    def __str__(self):
        return self.ean

    class Meta:
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"

    TYPES = [("lecturenote", "Skript"),
             ("printingquota", "Druckkontingent"),
             ("deposit", "Kautionsschein")]

    ean = models.CharField(max_length=20, verbose_name="EAN")
    type = models.CharField(max_length=256, choices=TYPES, null=True, verbose_name="Art")
    quantity = models.IntegerField(verbose_name="Anzahl")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Verkaufsvorgang")

    def price_single(self):
        return get_product(self.ean).price

    def name(self):
        return get_product(self.ean).name

    def price_total(self):
        return self.price_single() * self.quantity

    # return display name of instance type
    def type_str(self):
        return dict(self.TYPES)[self.type]
