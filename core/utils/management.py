from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from core.models import Author
from core.models import Deposit
from core.models import DepositNote
from core.models import LectureNote
from core.models import PrintingQuota
from core.models import Shift
from core.models import User

SETTINGS = {
    LectureNote: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["ean", "stock", "active"],
            },
            {
                "legend": _("properties"),
                "fields": [
                    "name",
                    "subject",
                    "price",
                    "study_grants",
                    "author",
                    "semester_start",
                    "semester_end",
                    "deposit",
                ],
            },
            {
                "legend": _("print settings"),
                "fields": ["color", "papersize", "sides", "printnotes", "file"],
            },
        ],
        "columns": {
            "fields": ["ean", "name", "subject", "active", "stock", "printnotes"],
            "styles": {
                "ean": ["width: 100px"],
                "active": ["width: 75px"],
                "stock": ["width: 50px"],
                "printnotes": ["width: 200px"],
            },
        },
    },
    Author: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["name", "mail"],
            },
        ],
        "columns": {
            "fields": ["name", "mail"],
        },
    },
    Deposit: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["ean", "name", "price"],
            },
        ],
        "columns": {
            "fields": ["ean", "name", "price"],
        },
    },
    DepositNote: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["number", "price"],
            },
            {
                "legend": _("sale"),
                "fields": ["sold_time", "sold_by"],
            },
            {
                "legend": pgettext_lazy("noun", "refund"),
                "fields": ["refunded_time", "refunded_by", "refundable"],
            },
        ],
        "columns": {
            "fields": ["number", "price", "sold_time", "refunded_time", "refundable"],
        },
    },
    PrintingQuota: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["ean", "pages", "price", "active"],
            },
        ],
        "columns": {
            "fields": ["ean", "pages", "price", "active"],
        },
    },
    Shift: {
        "fieldsets": [
            {
                "legend": None,
                "fields": ["time_start", "time_end", "vendor", "valid", "payout"],
            },
        ],
        "columns": {
            "fields": ["time_start", "time_end", "vendor", "valid", "payout"],
        },
    },
    User: {
        "fieldsets": [
            {
                "legend": _("user data"),
                "fields": [
                    "first_name",
                    "last_name",
                    "username",
                    "mail",
                    "password",
                    "password_repeat",
                ],
            },
            {
                "legend": _("permissions"),
                "fields": ["vendor", "referent", "financier", "admin"],
            },
        ],
        "columns": {
            "fields": ["username", "vendor", "referent", "financier", "admin"],
        },
    },
}


# return list of fields that are allowed for action or __all__ if all are allowed
def _get_allowed_fields(user, model, action):
    allowed_fields = []
    for group in user.groups:
        fields = model.permissions.get(action).get(group, [])
        if fields == "__all__":
            return fields
        allowed_fields += fields

    return allowed_fields


# get all fields that are configured for management
def _get_all_fields(model):
    all_fields = []
    for fieldset in SETTINGS.get(model).get("fieldsets"):
        all_fields += fieldset.get("fields")

    return all_fields


# return configured fieldsets that are allowed to be listed
def get_fieldsets(user, model):
    allowed_fields = _get_allowed_fields(user, model, "list")
    all_fieldsets = SETTINGS.get(model).get("fieldsets")

    # check if all fields are allowed
    if allowed_fields == "__all__":
        return all_fieldsets

    fieldsets = []
    for fieldset in all_fieldsets:
        fields = set(fieldset.get("fields"))
        for field in fields:
            if field not in allowed_fields:
                fieldset.get("fields").remove(field)
        if fieldset.get("fields"):
            fieldsets.append(fieldset)

    return fieldsets


# return configured fields that are allowed to be listed
def get_fields(user, model, action):
    all_fields = _get_all_fields(model)
    allowed_fields = _get_allowed_fields(user, model, action)

    # check if all fields are allowed
    if allowed_fields == "__all__":
        return all_fields

    return list(set(allowed_fields).intersection(set(all_fields)))


# return listable fields that are not allowed for action
def get_disabled_fields(user, model, action):
    all_fields = get_fields(user, model, "list")
    allowed_fields = get_fields(user, model, action)

    return set(all_fields) - set(allowed_fields)


# return configured columns that are allowed to be listed
def get_columns(user, model):
    all_columns = SETTINGS.get(model).get("columns").get("fields")
    allowed_columns = _get_allowed_fields(user, model, "list")

    # check if all fields are allowed
    if allowed_columns == "__all__":
        return all_columns

    return list(set(allowed_columns).intersection(set(all_columns)))


# return custom column styles
def get_column_style(model, field):
    return SETTINGS.get(model).get("columns").get("styles", {}).get(field, [])


# return listable columns that are not allowed for action
def get_disabled_columns(user, model):
    all_columns = get_columns(user, model)
    allowed_columns = get_fields(user, model, "update")

    return set(all_columns) - set(allowed_columns)


# return if user can access management interface of action
def is_allowed(user, model, action):
    # check if permissions are defined for model
    if not hasattr(model, "permissions"):
        return False

    if action == "delete":
        return user.is_authenticated and any(
            group in model.permissions.get("delete") for group in user.groups
        )

    return user.is_authenticated and _get_allowed_fields(user, model, action)
