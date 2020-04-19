from datetime import datetime

from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from core.forms import ShiftsForm
from core.models import Shift
from core.utils.functions import get_semesters


def semester_choices(user):
    # get users first shift
    first = Shift.objects.filter(vendor=user).order_by("time_start").first()

    if first.time_start.month in range(4, 10):
        start = f"S{first.time_start.year}"
    else:
        start = f"W{first.time_start.year - 1}"

    if timezone.now().month in range(4, 10):
        end = f"S{timezone.now().year}"
    else:
        end = f"W{timezone.now().year - 1}"

    # return choices
    return get_semesters(start, end)


def shifts(request):
    if not request.user.is_authenticated or not request.user.vendor:
        raise Http404

    form = ShiftsForm(semester_choices(request.user), request.POST)
    query = Shift.objects.filter(vendor=request.user).order_by("-time_start")

    action_semester = "semester" in request.POST and form.is_valid()

    # new semester choice selected
    if action_semester:
        semester = form.cleaned_data["semester"]

    # current semester
    else:
        semester = form.fields["semester"].choices[0][0]

    # filter query
    if semester.startswith("S"):
        query = query.filter(
            time_start__range=[
                timezone.make_aware(datetime(int(semester[1:]), 4, 1)),
                timezone.make_aware(datetime(int(semester[1:]), 10, 1)),
            ],
        )
    else:
        query = query.filter(
            time_start__range=[
                timezone.make_aware(datetime(int(semester[1:]), 10, 1)),
                timezone.make_aware(datetime(int(semester[1:]) + 1, 4, 1)),
            ],
        )

    # return all shifts of user ordered by time
    context = {
        "shifts": query,
        "form": form,
    }
    return render(request, "core/shifts.html", context)
