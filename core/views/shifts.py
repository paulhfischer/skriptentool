from django.http import Http404
from django.shortcuts import render

from core.models import Shift


def shifts(request):
    if request.user.is_authenticated and request.user.vendor:
        # return all shifts of user ordered by time
        context = {
            'shifts': Shift.objects.filter(vendor=request.user).order_by('-time_start')
        }
        return render(request, 'core/shifts.html', context)
    else:
        raise Http404
