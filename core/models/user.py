from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        username,
        email,
        first_name=None,
        last_name=None,
        password=None,
        vendor=False,
        financier=False,
        referent=False,
        admin=False,
        is_staff=False,
        default_location='MI',
    ):
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            vendor=vendor,
            financier=financier,
            referent=referent,
            is_staff=is_staff,
            is_superuser=admin,
            default_location=default_location,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, first_name=None, last_name=None, password=None):
        self.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            vendor=True,
            financier=True,
            referent=True,
            is_staff=True,
            is_superuser=True,
            default_location='MI',
        )


class User(AbstractBaseUser):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["username"]

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    
    MI = "MI"
    CH = "CH"
    
    LOCATIONS = [
        (MI, _("MI")),
        (CH, _("CH")),
    ]

    objects = UserManager()

    username = models.CharField(
        max_length=256,
        unique=True,
        validators=[
            RegexValidator(
                regex="@[a-z]+",
                message=_('Local usernames have to start with "@" and may only contain letters.'),
            ),
        ],
        verbose_name=_("username"),
    )

    email = models.EmailField(
        verbose_name=_("email"),
    )

    first_name = models.CharField(
        max_length=256,
        verbose_name=_("first name"),
    )

    last_name = models.CharField(
        max_length=256,
        verbose_name=_("last name"),
    )
    
    default_location = models.CharField(
    max_length=20,
    choices=LOCATIONS,
    default=MI,
    verbose_name=_("default location"),
    )

    vendor = models.BooleanField(
        default=False,
        verbose_name=_("vendor"),
    )

    referent = models.BooleanField(
        default=False,
        verbose_name=_("referent"),
    )

    financier = models.BooleanField(
        default=False,
        verbose_name=_("financier"),
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("is_staff"),
    )

    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_("is_superuser"),
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
    )

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_superuser_group = Group.objects.filter(name="is_superuser")[0]
        is_financier_group = Group.objects.filter(name="is_financier")[0]
        is_referent_group = Group.objects.filter(name="is_referent")[0]
        is_vendor_group = Group.objects.filter(name="is_vendor")[0]
        is_staff_group = Group.objects.filter(name="is_staff")[0]
        if self.is_superuser:
            self.vendor = True
            self.referent = True
            self.financier = True
            self.is_staff = True
            self.groups.add(is_superuser_group)
            self.groups.add(is_financier_group)
            self.groups.add(is_referent_group)
            self.groups.add(is_vendor_group)
            self.groups.add(is_staff_group)
        elif self.referent:
            self.vendor = True
            self.groups.add(is_referent_group)
            self.groups.add(is_vendor_group)
        elif self.vendor:
            self.groups.add(is_vendor_group)
        super().save(force_insert, force_update, using, update_fields)

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    permissions = {
        "list": {
            "is_referent": "__all__",
            "is_financier": "__all__",
        },
        "create": {},
        "update": {
            "is_referent": ["vendor", "referent", "default_location"],
            "is_financier": ["financier"],
            "is_superuser": ["is_superuser"],
        },
        "delete": [
            "is_superuser",
        ],
    }
