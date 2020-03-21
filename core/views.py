import csv
from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from core.forms import CashbookForm, SaleForm
from core.models import Balance, Cart, CartItem, CashBookEntry, DepositNote, LectureNote, Shift, get_product, get_type
from core.templatetags.filters import has_group


def catalogue(request):
    # return all active lecturenotes for each subject in alphabetical order
    context = {
        "mathematics_list": LectureNote.objects.filter(subject="M", active=True).order_by("name"),
        "physics_list": LectureNote.objects.filter(subject="P", active=True).order_by("name"),
        "informatics_list": LectureNote.objects.filter(subject="I", active=True).order_by("name"),
    }
    return render(request, "core/catalogue.html", context)


def shifts(request):
    if request.user.is_authenticated and has_group(request.user, "Verkäufer"):
        # return all shifts of user ordered by time
        context = {
            "shifts": Shift.objects.filter(vendor=request.user).order_by("-time_start")
        }
        return render(request, "core/shifts.html", context)
    else:
        raise Http404


def finance(request):
    if request.user.is_authenticated and has_group(request.user, "Finanzer"):
        start = timezone.make_aware(datetime.fromisoformat((datetime.today().date() - timedelta(weeks=1)).strftime("%Y-%m-%d")))
        end = timezone.make_aware(datetime.fromisoformat(datetime.today().date().strftime("%Y-%m-%d")) + timedelta(days=1))

        form = CashbookForm(request.POST)

        action_refresh = "refresh" in request.POST and form.is_valid()
        action_change = "change" in request.POST and form.is_valid()
        action_csv = "csv" in request.POST and form.is_valid()

        # "Aktualisieren"- or "CSV-Export"-button triggered
        # read input fields of date range
        if action_refresh or action_csv:
            start = timezone.make_aware(datetime.fromisoformat(form.cleaned_data["start"].strftime("%Y-%m-%d")))
            end = timezone.make_aware(datetime.fromisoformat(form.cleaned_data["end"].strftime("%Y-%m-%d")) + timedelta(days=1))

        # "Buchen"-button triggered
        if action_change:
            update = form.cleaned_data["update"]

            # update balance depending on action is deposit or withdrawal
            if update > 0:
                CashBookEntry.deposit(request.user, update)
                Balance.add_update(request.user, Balance.objects.latest("time").amount + update)
            elif update < 0:
                CashBookEntry.withdrawal(request.user, update)
                Balance.add_update(request.user, Balance.objects.latest("time").amount + update)

        # "CSV-Export"-button triggered
        if action_csv:
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attatchment; filename='kassenbuch.csv'"
            # create csv-file
            writer = csv.writer(response)
            writer.writerow(["Zeitpunkt", "Preis", "Beschreibung"])
            for cash_book_entry in CashBookEntry.objects.filter(time__range=[start, end]).values_list("time", "detail", "amount"):
                writer.writerow([cash_book_entry[0].strftime("%Y-%m-%d %H:%M:%S"), cash_book_entry[1], cash_book_entry[2]])
            return response

        context = {
            # prepopulated values for time range
            "cashbook_form": CashbookForm(initial={"start": start, "end": end - timedelta(days=1)}),
            # cashbook entries in selected time range
            "cashbook": sorted(list(chain(CashBookEntry.objects.filter(time__range=[start, end]).values_list("time", "user", "amount", "detail"),
                                          Balance.objects.filter(time__range=[start, end]).values_list("time", "user", "amount", "type"))),
                               key=lambda x: x[0], reverse=True),
            # current balance
            "balance": str(Balance.objects.latest("time").amount),
        }

        return render(request, "core/finance.html", context)
    else:
        raise Http404


def sale(request):
    if request.user.is_authenticated and has_group(request.user, "Verkäufer"):
        form = SaleForm(request.POST)

        # get current cart, return false otherwise (needed for permissions logic)
        try:
            cart = Cart.objects.get()
        except ObjectDoesNotExist:
            cart = False

        # check if cart is empty
        if hasattr(cart, "is_empty"):
            empty = cart.is_empty()
        else:
            empty = False

        # check if user is vendor of cart
        vendor = hasattr(request.user, "cart")

        # prepolpulate variables
        error = add_deposit_ean = remove_deposit_ean = remove_old_deposit_ean = remove_old_deposit_number = new_deposit_number = product_ean = None

        # permissions for front- and backend-check
        can_count = not Balance.objects.latest("time").counted and empty
        can_close = Balance.objects.latest("time").counted and empty
        can_next = cart and not empty
        can_open = Balance.objects.latest("time").counted and not cart
        can_order = vendor and not Balance.objects.latest("time").is_opening() or vendor and Balance.objects.latest("time").counted

        # button triggers
        action_count = "count" in request.POST and form.is_valid() and form.cleaned_data["balance"]
        action_close = "close" in request.POST and request.POST["close"]
        action_next = "next" in request.POST and request.POST["next"]
        action_open = "open" in request.POST
        action_order = "order" in request.POST and form.is_valid()
        action_has_deposit = "has_deposit" in request.POST and request.POST["has_deposit"]
        action_add_deposit = "add_deposit" in request.POST and request.POST["add_deposit"]
        action_remove_deposit = "remove_deposit" in request.POST and request.POST["remove_deposit"] and form.is_valid() and form.cleaned_data["deposit_number"]
        action_remove_old_deposit = "remove_old_deposit" in request.POST and request.POST["remove_old_deposit"]

        # balance is counted
        if can_count and action_count:
            Balance().count_latest(request.user, form.cleaned_data["balance"])

        # close cart
        # exception if other user already performed action but page has not been refreshed
        elif can_close and action_close:
            try:
                User.objects.get(username=request.POST["close"]).cart.close("closing")
            except ObjectDoesNotExist:
                pass

        # close cart and open next
        # exception if other user already performed action but page has not been refreshed
        elif can_next and action_next:
            try:
                User.objects.get(username=request.POST["next"]).cart.close("sale")
                cart = Cart(vendor=User.objects.get(username=request.POST["next"]))
                cart.save()
            except ObjectDoesNotExist:
                pass

        # open sale
        elif can_open and action_open:
            Cart(vendor=request.user).save()
            Balance().add_opening(request.user)
            Shift(time_start=timezone.now(), vendor=request.user, valid=False, payout=False).save()

        # sell item
        elif can_order and action_order:
            # add item to cart
            if form.cleaned_data["ean_add"]:
                # check if artlicle exists
                try:
                    product = get_product(form.cleaned_data["ean_add"])
                    product_type = get_type(form.cleaned_data["ean_add"])
                    # check if article is available for sale
                    if product.active:
                        # check if article needs deposit
                        try:
                            add_deposit_ean = product.get_deposit().ean
                            product_ean = form.cleaned_data["ean_add"]
                        except AttributeError:
                            # prevent sale of deposit
                            if product_type == "deposit":
                                error = "Kautionsscheine können nur mit Skript verkauft werden!"
                            else:
                                cart.add(form.cleaned_data["ean_add"])
                    else:
                        error = "Dieser Artikel steht nicht zum Verkauf!"
                except ObjectDoesNotExist:
                    error = "Dieser Artikel existiert nicht!"

            # remove item from cart
            elif form.cleaned_data["ean_remove"]:
                # check if artlicle exists
                try:
                    product_type = get_type(form.cleaned_data["ean_remove"])
                    # remove if not deposit, start refund process otherwise
                    if product_type == "deposit":
                        remove_deposit_ean = form.cleaned_data["ean_remove"]
                    else:
                        cart.remove(form.cleaned_data["ean_remove"])
                except ObjectDoesNotExist:
                    error = "Dieser Artikel existiert nicht!"

        # item sold before needed deposit but buyer already payed deposit
        elif can_order and action_has_deposit:
            cart.add(request.POST["has_deposit"])

        # item sold before needed deposit and buyer hasn't payed deposit yet
        elif can_order and action_add_deposit:
            # create new depositnote
            new_deposit_number = DepositNote.new_number()
            DepositNote(number=new_deposit_number,
                        price=get_product(request.POST["add_deposit"].split("|")[0]).price,
                        sold_by=request.user,
                        sold_time=timezone.now(),
                        refundable=False).save()
            # add deposit to cart
            cart.add(request.POST["add_deposit"].split("|")[0])
            # add item to cart
            cart.add(request.POST["add_deposit"].split("|")[1])

        # deposit should be refunded
        elif can_order and action_remove_deposit:
            deposit_number = form.cleaned_data["deposit_number"]
            deposit_ean = request.POST["remove_deposit"]
            # check if depositnote is in system
            if DepositNote.exists(deposit_number):
                # check if depositnote is allowed to be refunded
                if DepositNote.is_refundable(deposit_number):
                    # check if depositnote has already been refunded
                    if DepositNote.refunded(deposit_number):
                        error = "Der Kautionsschein " + deposit_number + " wurde bereits erstattet!"
                    else:
                        DepositNote.refund(deposit_number, request.user)
                        cart.remove(deposit_ean)
                else:
                    error = "Dieser Kautionsschein darf noch nicht erstattet werden!"
            # start deposit refund of old depositnote if user is "Referent"
            elif has_group(request.user, "Referent"):
                remove_old_deposit_number = deposit_number
                remove_old_deposit_ean = deposit_ean
            else:
                error = "Der Kautionsschein " + deposit_number + " kann nur von Referenten erstattet werden!"

        # depositnote not in system should be refunded
        elif can_order and action_remove_old_deposit and has_group(request.user, "Referent"):
            deposit_number = request.POST["remove_old_deposit"].split("|")[1]
            deposit_ean = request.POST["remove_old_deposit"].split("|")[0]
            DepositNote(number=deposit_number,
                        price=get_product(deposit_ean).price,
                        refunded_by=request.user,
                        refunded_time=timezone.now(),
                        refundable=True).save()
            cart.remove(deposit_ean)

        # cart could be modified in other methods, therefor refresh variables
        try:
            cart = Cart.objects.get()
        except ObjectDoesNotExist:
            cart = False

        if hasattr(cart, "is_empty"):
            empty = cart.is_empty()
        else:
            empty = False

        try:
            vendor = cart.vendor == request.user
        except AttributeError:
            vendor = False

        # Generate Context
        context = {
            "can_count": not Balance.objects.latest("time").counted and empty,
            "can_close": Balance.objects.latest("time").counted and empty,
            "can_next": cart and not empty,
            "can_open": Balance.objects.latest("time").counted and not cart,
            "can_order": vendor and not Balance.objects.latest("time").is_opening() or vendor and Balance.objects.latest("time").counted,
            "balance": str(Balance.objects.latest("time").amount),
            "form": SaleForm(initial={"balance": Balance.objects.latest("time").amount}),
            "vendor": vendor,
            "items": CartItem.objects.filter(cart=cart),
            "cart": cart,
            "error": error,
            "add_deposit_ean": add_deposit_ean,
            "remove_deposit_ean": remove_deposit_ean,
            "remove_old_deposit_ean": remove_old_deposit_ean,
            "remove_old_deposit_number": remove_old_deposit_number,
            "new_deposit_number": new_deposit_number,
            "product_ean": product_ean,
        }

        return render(request, "core/sale.html", context)
    else:
        raise Http404
