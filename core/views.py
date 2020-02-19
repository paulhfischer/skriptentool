from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from core.forms import SaleForm
from core.models import LectureNote, Cart, CartItem, Account


# Katalog
def catalogue(request):
    context = {
        "mathematics_list": LectureNote.objects.filter(subject="M", active=True).order_by("name"),
        "physics_list": LectureNote.objects.filter(subject="P", active=True).order_by("name"),
        "informatics_list": LectureNote.objects.filter(subject="I", active=True).order_by("name"),
    }

    return render(request, "core/catalogue.html", context)


# Finanz
def finance(request):
    context = {}
    return render(request, "core/finance.html", context)

    # DONE Formular bearbeiten
    # if own_cart: BuchenForm & button(order) DONE
    # if not counted: Kassenstand bestätigen & button(count) DONE
    # if not empty: Abschließen & button(next) DONE
    # if counted and empty: Eigenen schließen & button(close_own) DONE
    # if alien_cart: Fremden schließen & button(close_alien) DONE
    # if not user_cart and not alien_cart: Öffnen & button(open) DONE


# Verkauf
def sale(request):
    form = SaleForm(request.POST)
    if form.is_valid():  # TODO: Nothing required, only validate input fields
        valid = True
    else:
        valid = False

    if not Account.objects.latest("date").counted:  # Nicht gezählt
        if "count" in request.POST and valid:  # Kassenzählung
            if form.cleaned_data["balance"]:
                balance_new = form.cleaned_data["balance"]
                account_old = Account.objects.latest("date")
                if Account.objects.latest("date").type == "opening":
                    if balance_new == account_old.balance:  # Kassenstand korrekt
                        account_old.counted = True
                        account_old.save()
                    else:  # Kassenstand falsch
                        account_old.counted = True
                        account_old.balance = balance_new
                        account_old.save()
                else:
                    if balance_new == account_old.balance:  # Kassenstand korrekt
                        account_old.counted = True
                        account_old.save()
                        Account.objects.filter(type="sale").exclude(pk=account_old.pk).delete()
                    else:  # Kassenstand falsch
                        Account(changed_by=request.user, balance=balance_new, counted=True, type="correction").save()
                        Account.objects.filter(type="sale").delete()

    if Cart.objects.filter(vendor=request.user.id).exists():  # Eigener Warenkorb existiert
        own_cart = Cart.objects.get(vendor=request.user.id)

        if Account.objects.latest("date").type != "opening" or Account.objects.latest("date").counted:
            if "order" in request.POST and valid:  # Buchungsvorgang
                if form.cleaned_data["ean_add"]:
                    own_cart.add(form.cleaned_data["ean_add"])
                if form.cleaned_data["ean_remove"]:
                    own_cart.remove(form.cleaned_data["ean_remove"])

        if not own_cart.is_empty():
            if "next_own" in request.POST:  # Eigenen Verkaufsvorgang beenden und neuen öffnen
                own_cart.close("sale")
                own_cart = Cart(vendor=request.user)
                own_cart.save()

        if Account.objects.latest("date").counted and own_cart.is_empty():
            if "close_own" in request.POST:  # Eigenen Verkauf schließen
                own_cart.close("closing")

    elif Cart.objects.exists():  # Fremder Warenkorb existiert
        alien_cart = Cart.objects.get()

        if not alien_cart.is_empty():
            if "next_alien" in request.POST:  # Fremden Verkaufsvorgang beenden und neuen öffnen
                alien_cart.close("sale")
                alien_cart = Cart(vendor=User.objects.get(username=request.POST.get("next_alien")))
                alien_cart.save()

        if Account.objects.latest("date").counted and alien_cart.is_empty():
            if "close_alien" in request.POST:  # Fremden Verkauf schließen
                alien_cart.close("closing")

    else:  # Kein Warenkorb existiert
        if "open" in request.POST:  # Verkaufsvorgang starten
            Cart(vendor=request.user).save()
            Account(changed_by=request.user, balance=Account.objects.latest("date").balance, counted=False,
                    type="opening").save()

    context = {
        "balance": str(Account.objects.latest("date").balance),
        "form": SaleForm(initial={"balance": Account.objects.latest("date").balance}),
        "last_balance": Account.objects.latest("date"),
    }

    try:
        context.update({"own_cart": Cart.objects.get(vendor=request.user)})
    except ObjectDoesNotExist:
        pass

    try:
        context.update({"alien_cart": Cart.objects.exclude(vendor=request.user).get()})
    except ObjectDoesNotExist:
        pass

    try:
        context.update({"items": CartItem.objects.filter(cart=own_cart)})
    except UnboundLocalError:
        pass

    return render(request, "core/sale.html", context)
