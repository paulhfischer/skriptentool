import csv
from datetime import datetime
from datetime import timedelta
from itertools import chain

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from core.forms import CashbookForm
from core.models import Balance
from core.models import CashBookEntry


def get_balances(start, end):
    # convert choices field to display_value
    balances = []
    for balance in Balance.objects.filter(time__range=[start, end]).values_list(
        "time",
        "user",
        "amount",
        "type",
    ):
        type_display = {k: v for k, v in Balance.TYPES}[balance[-1]]
        balances.append(list(balance[:-1]) + [type_display])
    return balances


def get_cashbookentries(start, end):
    values = []
    for cash_book_entry in CashBookEntry.objects.filter(time__range=[start, end]):
        values.append(
            (
                cash_book_entry.time,
                cash_book_entry.user.pk,
                cash_book_entry.amount,
                cash_book_entry.text,
            ),
        )
    return values


def finance(request):
    if not request.user.is_authenticated or not request.user.financier:
        raise Http404

    start = timezone.make_aware(
        datetime.fromisoformat(
            (datetime.today().date() - timedelta(weeks=1)).strftime("%Y-%m-%d"),
        ),
    )
    end = timezone.make_aware(
        datetime.fromisoformat(datetime.today().date().strftime("%Y-%m-%d")) + timedelta(days=1),
    )

    form = CashbookForm(request.POST)

    action_refresh = "refresh" in request.POST and form.is_valid()
    action_change = "change" in request.POST and form.is_valid()
    action_csv = "csv" in request.POST and form.is_valid()

    # 'Aktualisieren'- or 'CSV-Export'-button triggered
    # read input fields of date range
    if action_refresh or action_csv:
        start = timezone.make_aware(
            datetime.fromisoformat(form.cleaned_data["start"].strftime("%Y-%m-%d")),
        )
        end = timezone.make_aware(
            datetime.fromisoformat(form.cleaned_data["end"].strftime("%Y-%m-%d"))
            + timedelta(days=1),
        )

    # 'Buchen'-button triggered
    if action_change:
        update = form.cleaned_data["update"]

        # update balance depending on action is deposit or withdrawal
        if update > 0:
            CashBookEntry.deposit(request.user, update)
            Balance.add_update(request.user, Balance.objects.latest("time").amount + update)
        elif update < 0:
            CashBookEntry.withdrawal(request.user, update)
            Balance.add_update(request.user, Balance.objects.latest("time").amount + update)

    # 'CSV-Export'-button triggered
    if action_csv:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attatchment; filename="kassenbuch.csv"'
        # create csv-file
        writer = csv.writer(response)
        writer.writerow(["Zeitpunkt", "Beschreibung", "Preis"])
        for cash_book_entry in CashBookEntry.objects.filter(
            time__range=[start, end],
        ).values_list("time", "detail", "amount"):
            writer.writerow(
                [
                    cash_book_entry[0].strftime("%Y-%m-%d %H:%M:%S"),
                    cash_book_entry[1],
                    cash_book_entry[2],
                ],
            )
        return response

    context = {
        # prepopulated values for time range
        "cashbook_form": CashbookForm(initial={"start": start, "end": end - timedelta(days=1)}),
        # cashbook entries in selected time range
        "cashbook": sorted(
            chain(get_cashbookentries(start, end), get_balances(start, end)),
            key=lambda x: x[0],
            reverse=True,
        ),
        # current balance
        "balance": str(Balance.objects.latest("time").amount),
    }

    return render(request, "core/finance.html", context)
