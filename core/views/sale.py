from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from core.forms import SaleForm
from core.models import Balance, Cart, CartItem, DepositNote, Shift, User, get_product, get_type


def sale(request):
    if request.user.is_authenticated and request.user.is_vendor:
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
            elif request.user.is_referent:
                remove_old_deposit_number = deposit_number
                remove_old_deposit_ean = deposit_ean
            else:
                error = "Der Kautionsschein " + deposit_number + " kann nur von Referenten erstattet werden!"

        # depositnote not in system should be refunded
        elif can_order and action_remove_old_deposit and request.user.is_referent:
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
