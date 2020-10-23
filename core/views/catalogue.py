from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.models import LectureNote


def render_table(lecturenotes, subject):
    context = {
        "lecturenotes": lecturenotes,
        "subject": subject,
    }

    return render_to_string("core/widgets/catalogue_table.html", context)


def catalogue(request):
    # return all active lecturenotes for each subject in alphabetical order
    context = {
        "mathematics_list": render_table(
            LectureNote.objects.filter(subject="M", active=True).order_by("name"),
            _("mathematics"),
        ),
        "physics_list": render_table(
            LectureNote.objects.filter(subject="P", active=True).order_by("name"),
            _("physics"),
        ),
        "informatics_list": render_table(
            LectureNote.objects.filter(subject="I", active=True).order_by("name"),
            _("informatics"),
        ),
    }

    return render(request, "core/catalogue.html", context)
