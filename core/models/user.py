from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        username,
        mail,
        first_name,
        last_name,
        password,
        vendor,
        financier,
        referent,
        admin,
    ):
        user = self.model(
            username=username,
            mail=mail,
            first_name=first_name,
            last_name=last_name,
            vendor=vendor,
            financier=financier,
            referent=referent,
            admin=admin,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, mail, first_name, last_name, password):
        self.create_user(
            username=username,
            mail=mail,
            first_name=first_name,
            last_name=last_name,
            password=password,
            vendor=True,
            financier=True,
            referent=True,
            admin=True,
        )


class User(AbstractBaseUser):
    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"
        ordering = ["username"]

    EMAIL_FIELD = "mail"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["mail", "first_name", "last_name"]

    objects = UserManager()

    username = models.CharField(
        max_length=256,
        unique=True,
        validators=[
            RegexValidator(
                regex="@[a-z]+",
                message=(
                    "Lokale Benutzernamen müssen mit @ beginnen und dürfen nur Buchstaben "
                    "enthalten."
                ),
            ),
        ],
        verbose_name="Benutzername",
    )

    mail = models.EmailField(
        verbose_name="E-Mail-Adresse",
    )

    first_name = models.CharField(
        max_length=256,
        verbose_name="Vorname",
    )

    last_name = models.CharField(
        max_length=256,
        verbose_name="Nachname",
    )

    vendor = models.BooleanField(
        default=False,
        verbose_name="Verkäufer",
    )

    referent = models.BooleanField(
        default=False,
        verbose_name="Referent",
    )

    financier = models.BooleanField(
        default=False,
        verbose_name="Finanzer",
    )

    admin = models.BooleanField(
        default=False,
        verbose_name="Admin",
    )

    def clean(self):
        super().clean()
        self.mail = self.__class__.objects.normalize_email(self.mail)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.mail], **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.admin:
            self.vendor = True
            self.referent = True
            self.financier = True
        elif self.referent:
            self.vendor = True
        super().save(force_insert, force_update, using, update_fields)

    @property
    def groups(self):
        groups = []
        if self.vendor:
            groups.append("is_vendor")
        if self.referent:
            groups.append("is_referent")
        if self.financier:
            groups.append("is_financier")
        if self.admin:
            groups.append("is_admin")
        return groups

    # allow backend access for admins only
    @property
    def is_staff(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin

    def has_module_perms(self, app_label):
        return self.admin

    def has_perm(self, perm, obj=None):
        return self.admin

    permissions = {
        "list": {
            "is_referent": "__all__",
        },
        "create": {
            "is_admin": "__all__",
        },
        "update": {
            "is_referent": ["vendor", "referent"],
            "is_financier": ["financier"],
            "is_admin": ["admin"],
        },
        "delete": [
            "is_admin",
        ],
    }
