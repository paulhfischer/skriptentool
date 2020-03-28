from django.shortcuts import render

from core.models import LectureNote


def catalogue(request):
    # return all active lecturenotes for each subject in alphabetical order
    context = {
        "mathematics_list": LectureNote.objects.filter(subject="M", active=True).order_by("name"),
        "physics_list": LectureNote.objects.filter(subject="P", active=True).order_by("name"),
        "informatics_list": LectureNote.objects.filter(subject="I", active=True).order_by("name"),
    }
    return render(request, "core/catalogue.html", context)
