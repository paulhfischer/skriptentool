from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.mail import mail_admins
from django.template.defaultfilters import safe
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from core.models import LectureNote
from core.models.products import generate_cover
from core.models.products import generate_order

admin.site.unregister(Group)


def create_order(modeladmin, request, queryset):
    for lecturenote in queryset:
        generate_order(lecturenote)


create_order.short_description = capfirst(_("generate orders"))


def create_cover(modeladmin, request, queryset):
    for lecturenote in queryset:
        generate_cover(lecturenote)


create_cover.short_description = capfirst(_("generate covers"))


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


class LectureNoteAdmin(Admin):
    actions = [create_order, create_cover]


for model in apps.get_app_config("core").get_models():
    if model == LectureNote:
        admin.site.register(model, LectureNoteAdmin)
    else:
        admin.site.register(model, Admin)
