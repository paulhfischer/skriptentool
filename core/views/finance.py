import csv
from collections import Counter
from datetime import datetime
from datetime import timedelta
from itertools import chain

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from core.forms import CashbookForm
from core.models import Balance
from core.models import CashBookEntry
from core.models.products import get_type


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
        datetime.fromisoformat((datetime.today().date() - timedelta(weeks=1)).strftime("%Y-%m-%d")),
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
        comment = form.cleaned_data["comment"]

        # update balance depending on action is deposit or withdrawal
        if update > 0:
            CashBookEntry.deposit(request.user, update, comment)
            Balance.add_update(request.user, Balance.objects.latest("time").amount + update)
        elif update < 0:
            CashBookEntry.withdrawal(request.user, update, comment)
            Balance.add_update(request.user, Balance.objects.latest("time").amount + update)

    # 'CSV-Export'-button triggered
    if action_csv:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = format_lazy(
            'attatchment; filename="{}.csv"',
            _("cashbook"),
        )

        cash_book_entries = CashBookEntry.objects.filter(time__range=[start, end])

        writer = csv.writer(response)
        writer.writerow(
            [
                _("date"),
                _("lecture notes"),
                _("deposits"),
                _("printing quotas"),
                _("corrections"),
                _("transactions"),
            ],
        )
        for day in set(cash_book_entries.values_list("time__date", flat=True)):
            counter = Counter()
            for cash_book_entry in cash_book_entries.filter(time__date=day):
                if cash_book_entry.type == CashBookEntry.SALE:
                    type = get_type(cash_book_entry.detail)
                    if type == "lecturenote":
                        counter["lecture notes"] += cash_book_entry.amount
                        continue
                    if type == "deposit":
                        counter["deposits"] += cash_book_entry.amount
                        continue
                    if type == "printingquota":
                        counter["printing quotas"] += cash_book_entry.amount
                        continue
                if cash_book_entry.type == CashBookEntry.CORRECTION:
                    counter["corrections"] += cash_book_entry.amount
                    continue
                if cash_book_entry.type == CashBookEntry.WITHDRAWAL:
                    counter["transactions"] += cash_book_entry.amount
                    continue
                if cash_book_entry.type == CashBookEntry.DEPOSIT:
                    counter["transactions"] += cash_book_entry.amount
                    continue

            writer.writerow(
                [
                    day.strftime("%Y-%m-%d"),
                    counter["lecture notes"],
                    counter["deposits"],
                    counter["printing quotas"],
                    counter["corrections"],
                    counter["transactions"],
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
