from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.mail import mail_admins
from django.template.defaultfilters import safe
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from skriptentool import settings

admin.site.unregister(Group)


class Admin(admin.ModelAdmin):
    def log_addition(self, request, object, message):
        with translation.override(settings.LANGUAGE_CODE):
            mail_admins(
                subject=_("Changes in admin interface"),
                message=render_to_string(
                    "core/mail/admin_log.txt",
                    {
                        "username": request.user.username,
                        "class": object.__class__.__name__,
                        "object": object,
                        "message": safe(message),
                    },
                ),
            )

    def log_change(self, request, object, message):
        with translation.override(settings.LANGUAGE_CODE):
            mail_admins(
                subject=_("Changes in admin interface"),
                message=render_to_string(
                    "core/mail/admin_log.txt",
                    {
                        "username": request.user.username,
                        "class": object.__class__.__name__,
                        "object": object,
                        "message": safe(message),
                    },
                ),
            )

    def log_deletion(self, request, object, object_repr):
        with translation.override(settings.LANGUAGE_CODE):
            mail_admins(
                subject=_("Changes in admin interface"),
                message=render_to_string(
                    "core/mail/admin_log.txt",
                    {
                        "username": request.user.username,
                        "class": object.__class__.__name__,
                        "object": object,
                        "message": safe("[{'deleted': {}}]"),
                    },
                ),
            )


for model in apps.get_app_config("core").get_models():
    admin.site.register(model, Admin)
