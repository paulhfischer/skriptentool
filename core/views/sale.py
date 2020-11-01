from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import SaleForm
from core.models import Balance
from core.models import Cart
from core.models import CartItem
from core.models import DepositNote
from core.models import get_product
from core.models import get_type
from core.models import Shift
from core.models import User
from core.models.products import PrintingQuota
from core.utils.printing_quota import add_balance
from core.utils.printing_quota import get_balance


def sale(request):
    if not request.user.is_authenticated or not request.user.vendor:
        raise Http404

    form = SaleForm(request.POST)

    # get current cart, return false otherwise (needed for permissions logic)
    cart = Cart.objects.first()

    # check if cart is empty
    empty = getattr(cart, "is_empty", False)

    # check if user is vendor of cart
    vendor = hasattr(request.user, "cart")

    # prepolpulate variables
    error = (
        add_deposit_ean
    ) = (
        remove_deposit_ean
    ) = (
        remove_old_deposit_ean
    ) = (
        remove_old_deposit_number
    ) = (
        new_deposit_number
    ) = add_quota_ean = remove_quota_ean = new_account_balance = product_ean = None

    # permissions for front- and backend-check
    can_count = not Balance.objects.latest("time").counted and empty
    can_close = Balance.objects.latest("time").counted and empty
    can_next = cart and not empty
    can_open = Balance.objects.latest("time").counted and not cart
    can_order = (
        vendor
        and not Balance.objects.latest("time").is_opening
        or vendor
        and Balance.objects.latest("time").counted
    )

    # button triggers
    action_count = "count" in request.POST and form.is_valid() and form.cleaned_data["balance"]
    action_close = "close" in request.POST and request.POST["close"]
    action_next = "next" in request.POST and request.POST["next"]
    action_open = "open" in request.POST
    action_order = "order" in request.POST and form.is_valid()
    action_has_deposit = "has_deposit" in request.POST and request.POST["has_deposit"]
    action_add_deposit = "add_deposit" in request.POST and request.POST["add_deposit"]
    action_remove_deposit = (
        "remove_deposit" in request.POST
        and request.POST["remove_deposit"]
        and form.is_valid()
        and form.cleaned_data["deposit_number"]
    )
    action_remove_old_deposit = (
        "remove_old_deposit" in request.POST and request.POST["remove_old_deposit"]
    )
    action_add_quota = (
        "add_quota" in request.POST
        and request.POST["add_quota"]
        and form.is_valid()
        and form.cleaned_data["account_number"]
    )
    action_remove_quota = (
        "remove_quota" in request.POST
        and request.POST["remove_quota"]
        and form.is_valid()
        and form.cleaned_data["account_number"]
    )

    # count balance
    if can_count and action_count:
        Balance().count_latest(request.user, form.cleaned_data["balance"])

    # close cart
    # exception if other user already performed action but page has not been refreshed
    elif can_close and action_close:
        User.objects.get(username=request.POST["close"]).cart.close()

    # close cart and open next
    # exception if other user already performed action but page has not been refreshed
    elif can_next and action_next:
        try:
            User.objects.get(username=request.POST["next"]).cart.close(reason="sale")
            Cart(vendor=User.objects.get(username=request.POST["next"])).save()
        except ObjectDoesNotExist:
            pass

    # open sale
    elif can_open and action_open:
        Cart(vendor=request.user).save()
        Balance().add_opening(request.user)
        Shift(vendor=request.user).save()

    # sell item
    elif can_order and action_order:
        if form.cleaned_data["ean_add"]:
            ean = form.cleaned_data["ean_add"]

            # check if artlicle exists
            try:
                product = get_product(ean)
                product_type = get_type(ean)

                # prevent sale of deposit
                if product_type == "deposit":
                    error = _("Deposit notes can only be sold with a lecture note.")

                # check if article is available for sale
                elif product.active:
                    # check if article needs deposit
                    try:
                        add_deposit_ean = product.deposit.ean
                        product_ean = ean
                    except AttributeError:
                        if product_type == "printingquota":
                            add_quota_ean = ean
                        else:
                            cart.add(ean)
                else:
                    error = _("This item isn't for sale.")
            except ObjectDoesNotExist:
                error = _("This item doesn't exist.")

        elif form.cleaned_data["ean_remove"]:
            ean = form.cleaned_data["ean_remove"]

            # check if artlicle exists
            try:
                product_type = get_type(ean)

                # remove if not deposit, start refund process otherwise
                if product_type == "deposit":
                    remove_deposit_ean = ean
                if product_type == "printingquota":
                    remove_quota_ean = ean
                else:
                    cart.remove(ean)
            except ObjectDoesNotExist:
                error = _("This item doesn't exist.")

    # item sold before needed deposit but buyer already paid deposit
    elif can_order and action_has_deposit:
        cart.add(request.POST["has_deposit"])

    # item sold before needed deposit and buyer hasn't paid deposit yet
    elif can_order and action_add_deposit:
        # create new depositnote
        new_deposit_number = DepositNote.new_number()
        DepositNote(
            number=new_deposit_number,
            price=get_product(request.POST["add_deposit"].split("|")[0]).price,
            sold_by=request.user,
            sold_time=timezone.now(),
            refundable=False,
        ).save()
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
                    error = _("The deposit note %(num)s has alredy been refunded.") % {
                        "num": deposit_number,
                    }
                else:
                    DepositNote.refund(deposit_number, request.user)
                    cart.remove(deposit_ean)
            else:
                error = _("This deposit note mustn't be refunded yet.")
        # start deposit refund of old depositnote if user is 'Referent'
        elif request.user.referent:
            remove_old_deposit_number = deposit_number
            remove_old_deposit_ean = deposit_ean
        else:
            error = _("The deposit note %(num)s can only be refunded by a referent.") % {
                "num": deposit_number,
            }

    # depositnote not in system should be refunded
    elif can_order and action_remove_old_deposit and request.user.referent:
        deposit_number = request.POST["remove_old_deposit"].split("|")[1]
        deposit_ean = request.POST["remove_old_deposit"].split("|")[0]
        DepositNote(
            number=deposit_number,
            price=get_product(deposit_ean).price,
            refunded_by=request.user,
            refunded_time=timezone.now(),
            refundable=True,
        ).save()
        cart.remove(deposit_ean)

    # printing quota should be added
    elif can_order and action_add_quota:
        account_number = form.cleaned_data["account_number"]
        quota_ean = request.POST["add_quota"]
        pages = PrintingQuota.objects.get(ean=quota_ean).pages
        try:
            # add balance to customer's account
            new_account_balance = [f"{get_balance(request.user, account_number):.2f}"]
            add_balance(request.user, account_number, pages)
            new_account_balance += [f"{get_balance(request.user, account_number):.2f}"]

            # add product to cart
            cart.add(quota_ean)
        except TypeError:
            # retry process
            add_quota_ean = quota_ean

    # printing quota should be removed
    elif can_order and action_remove_quota:
        account_number = form.cleaned_data["account_number"]
        quota_ean = request.POST["remove_quota"]
        pages = PrintingQuota.objects.get(ean=quota_ean).pages
        try:
            # remove balance to customer's account
            new_account_balance = [f"{get_balance(request.user, account_number):.2f}"]
            add_balance(request.user, account_number, -pages)
            new_account_balance += [f"{get_balance(request.user, account_number):.2f}"]

            # add product to cart
            cart.remove(quota_ean)
        except TypeError:
            # retry process
            remove_quota_ean = quota_ean

    # cart could be modified in other methods, therefor refresh variables
    cart = Cart.objects.first() or False
    empty = getattr(cart, "is_empty", False)
    vendor = getattr(cart, "vendor", False) == request.user

    # Generate Context
    context = {
        "can_count": not Balance.objects.latest("time").counted and empty,
        "can_close": Balance.objects.latest("time").counted and empty,
        "can_next": cart and not empty,
        "can_open": Balance.objects.latest("time").counted and not cart,
        "can_order": vendor
        and not Balance.objects.latest("time").is_opening
        or vendor
        and Balance.objects.latest("time").counted,
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
        "remove_quota_ean": remove_quota_ean,
        "add_quota_ean": add_quota_ean,
        "new_account_balance": new_account_balance,
        "product_ean": product_ean,
    }

    return render(request, "core/sale.html", context)
