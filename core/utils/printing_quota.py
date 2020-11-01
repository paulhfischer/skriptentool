import requests
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.text import capfirst
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from requests.exceptions import ConnectTimeout
from requests.exceptions import HTTPError
from requests.models import HTTPBasicAuth

from core.models.printingquota_log import PrintingQuotaLog
from skriptentool import config
from skriptentool import settings


def get_balance(vendor, number):
    log = PrintingQuotaLog(
        user=vendor,
        account=number,
        type=PrintingQuotaLog.GET,
        status=PrintingQuotaLog.PENDING,
    )
    log.save()

    try:
        request = requests.get(
            f"https://qpilot.rbg.tum.de:9779/balance/for-card-number/{number}",
            auth=HTTPBasicAuth(config.QPILOT_USERNAME, config.QPILOT_PASSWORD),
            timeout=5,
        )
    except ConnectTimeout:
        log.status = PrintingQuotaLog.TIMEOUT
        log.save()

        raise TypeError

    try:
        request.raise_for_status()
    except HTTPError as error:
        if request.status_code == 401:
            log.status = PrintingQuotaLog.UNAUTHORIZED
            log.save()

            raise TypeError

        if request.status_code == 422:
            log.status = PrintingQuotaLog.UNKNOWN_NUMBER
            log.save()

            raise TypeError

        raise error

    log.status = PrintingQuotaLog.SUCCESS
    log.save()

    return round(float(request.json()["totalBalance"]), 2)


def add_balance(vendor, number, amount):
    log = PrintingQuotaLog(
        user=vendor,
        account=number,
        type=PrintingQuotaLog.ADD,
        status=PrintingQuotaLog.PENDING,
    )
    log.save()

    try:
        request = requests.post(
            f"https://qpilot.rbg.tum.de:9779/transfer/for-card-number/{number}/create",
            data={
                "reasonForTransfer": "Skriptentool | testing" if config.DEBUG else "Skriptentool",
                "amountOfMoney": amount,
            },
            auth=HTTPBasicAuth(config.QPILOT_USERNAME, config.QPILOT_PASSWORD),
            timeout=5,
        )
    except ConnectTimeout:
        log.status = PrintingQuotaLog.TIMEOUT
        log.save()

        raise TypeError

    try:
        request.raise_for_status()
    except HTTPError as error:
        if request.status_code == 401:
            log.status = PrintingQuotaLog.UNAUTHORIZED
            log.save()

            raise TypeError

        if request.status_code == 422:
            log.status = PrintingQuotaLog.UNKNOWN_NUMBER
            log.save()

            raise TypeError

        raise error

    log.status = PrintingQuotaLog.SUCCESS
    log.save()

    with translation.override(settings.LANGUAGE_CODE):
        send_mail(
            subject=format_lazy(
                "[Skriptentool] {}",
                capfirst(_("printing quota booked")),
            ),
            message=render_to_string(
                "core/mail/printing_quota_booked.txt",
                {"vendor": vendor, "number": number, "amount": amount},
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=config.REFERENT_EMAILS,
        )
