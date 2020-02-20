import csv
from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render

from core.forms import CashbookForm, SaleForm
from core.models import Balance, Cart, CartItem, CashBookEntry, LectureNote, get_product, get_type
from core.templatetags.filters import has_group


# Katalog
def catalogue(request):
    context = {"mathematics_list": LectureNote.objects.filter(subject = "M", active = True).order_by("name"),
               "physics_list": LectureNote.objects.filter(subject = "P", active = True).order_by("name"),
               "informatics_list": LectureNote.objects.filter(subject = "I", active = True).order_by("name"), }

    return render(request, "core/catalogue.html", context)


# Finanz
def finance(request):
    if request.user.is_authenticated and has_group(request.user, "Finanzer"):
        start = datetime.today().date() - timedelta(weeks = 1)
        end = datetime.today().date()

        form = CashbookForm(request.POST)
        if form.is_valid():  # TODO
            valid = True
        else:
            valid = False

        if "refresh" in request.POST or "csv" in request.POST and valid:
            start = form.cleaned_data["start"]
            end = form.cleaned_data["end"]

        if "change" in request.POST and valid:
            update = form.cleaned_data["update"]
            if update > 0:
                CashBookEntry.deposit(request.user, update)
            elif update < 0:
                CashBookEntry.withdrawal(request.user, update)
            Balance.add_update(request.user, Balance.objects.latest("time").amount + update)

        if "csv" in request.POST and valid:
            response = HttpResponse(content_type = "text/csv")
            response["Content-Disposition"] = "attatchment; filename='kassenbuch.csv'"
            writer = csv.writer(response)
            writer.writerow(["Zeitpunkt", "Preis", "Beschreibung"])
            for foo in CashBookEntry.objects.filter(time__range = [start.strftime("%Y-%m-%d"),
                                                                   (end + timedelta(days = 1)).strftime(
                                                                       "%Y-%m-%d")]).values_list("time", "amount",
                                                                                                 "detail"):
                writer.writerow([foo[0].strftime("%Y-%m-%d %H:%M:%S"), foo[1], foo[2]])
            return response

        context = {"cashbook_form": CashbookForm(initial = {"start": start, "end": end}), "cashbook": sorted(list(chain(
            CashBookEntry.objects.filter(time__range = [start.strftime("%Y-%m-%d"),
                                                        (end + timedelta(days = 1)).strftime("%Y-%m-%d")]).values_list(
                "time", "user", "amount", "detail"), Balance.objects.filter(time__range = [start.strftime("%Y-%m-%d"), (
                    end + timedelta(days = 1)).strftime("%Y-%m-%d")]).values_list("time", "user", "amount", "type"))),
            key = lambda x: x[0], reverse = True), "balance": str(Balance.objects.latest("time").amount),
                   "test": form.cleaned_data["update"], }

        return render(request, "core/finance.html", context)
    else:
        return HttpResponse("")


# Verkauf
def sale(request):
    if request.user.is_authenticated and has_group(request.user, "Verkäufer"):
        form = SaleForm(request.POST)
        if form.is_valid():  # TODO
            valid = True
        else:
            valid = False

        if not Balance.objects.latest("time").counted:  # Nicht gezählt
            if "count" in request.POST and valid:  # Kassenzählung
                if form.cleaned_data["balance"]:
                    Balance().count_latest(request.user, form.cleaned_data["balance"])

        if Cart.objects.filter(vendor = request.user.id).exists():  # Eigener Warenkorb existiert
            own_cart = Cart.objects.get(vendor = request.user.id)

            if not Balance.objects.latest("time").is_opening() or Balance.objects.latest("time").counted:
                if "order" in request.POST and valid:  # Buchungsvorgang
                    if form.cleaned_data["ean_add"]:
                        try:  # Überprüfe ob Kaution benötigt wird
                            add_deposit = get_product(form.cleaned_data["ean_add"]).get_deposit().ean
                            deposit_item = form.cleaned_data["ean_add"]
                        except AttributeError:
                            if get_type(form.cleaned_data["ean_add"]) != "deposit":
                                own_cart.add(form.cleaned_data["ean_add"])
                    if form.cleaned_data["ean_remove"]:
                        if get_type(form.cleaned_data["ean_remove"]) == "deposit":  # Überprüfe ob Kautionsauszahlung
                            remove_deposit = form.cleaned_data["ean_remove"]
                        else:
                            own_cart.remove(form.cleaned_data["ean_remove"])
                if "has_deposit" in request.POST and valid:  # Kautionsschein vorhanden
                    if request.POST["has_deposit"]:
                        own_cart.add(request.POST["has_deposit"].split("|")[0])
                if "add_deposit" in request.POST and valid:  # Kautionseinzahlung
                    if request.POST["add_deposit"]:
                        # TODO store deposit number -> create new and output
                        own_cart.add(request.POST["add_deposit"].split("|")[0])
                        own_cart.add(request.POST["add_deposit"].split("|")[1])
                if "remove_deposit" in request.POST and valid:  # Kautionsauszahlung
                    if request.POST["remove_deposit"]:
                        # TODO store deposit number -> form.cleaned_data["deposit"]
                        own_cart.remove(request.POST["remove_deposit"])

            if not own_cart.is_empty():
                if "next_own" in request.POST:  # Eigenen Verkaufsvorgang beenden und neuen öffnen
                    own_cart.close("sale")
                    own_cart = Cart(vendor = request.user)
                    own_cart.save()

            if Balance.objects.latest("time").counted and own_cart.is_empty():
                if "close_own" in request.POST:  # Eigenen Verkauf schließen
                    own_cart.close("closing")

        elif Cart.objects.exists():  # Fremder Warenkorb existiert
            alien_cart = Cart.objects.get()

            if not alien_cart.is_empty():
                if "next_alien" in request.POST:  # Fremden Verkaufsvorgang beenden und neuen öffnen
                    alien_cart.close("sale")
                    alien_cart = Cart(vendor = User.objects.get(username = request.POST.get("next_alien")))
                    alien_cart.save()

            if Balance.objects.latest("time").counted and alien_cart.is_empty():
                if "close_alien" in request.POST:  # Fremden Verkauf schließen
                    alien_cart.close("closing")

        else:  # Kein Warenkorb existiert
            if "open" in request.POST:  # Verkaufsvorgang starten
                Cart(vendor = request.user).save()
                Balance().add_opening(request.user)

        context = {"balance": str(Balance.objects.latest("time").amount),
                   "form": SaleForm(initial = {"balance": Balance.objects.latest("time").amount}),
                   "last_balance": Balance.objects.latest("time"), }

        try:
            context.update({"own_cart": Cart.objects.get(vendor = request.user)})
        except ObjectDoesNotExist:
            pass

        try:
            context.update({"alien_cart": Cart.objects.exclude(vendor = request.user).get()})
        except ObjectDoesNotExist:
            pass

        try:
            # noinspection PyUnboundLocalVariable
            context.update({"items": CartItem.objects.filter(cart = own_cart)})
        except UnboundLocalError:
            pass

        try:
            # noinspection PyUnboundLocalVariable
            context.update({"add_deposit": add_deposit})
        except UnboundLocalError:
            pass

        try:
            # noinspection PyUnboundLocalVariable
            context.update({"remove_deposit": remove_deposit})
        except UnboundLocalError:
            pass

        try:
            # noinspection PyUnboundLocalVariable
            context.update({"deposit_item": deposit_item})
        except UnboundLocalError:
            pass

        return render(request, "core/sale.html", context)
    else:
        return HttpResponse("")
