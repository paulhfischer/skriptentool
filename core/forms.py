from django import forms
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class SaleForm(forms.Form):
    ean_add = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    ean_remove = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    balance = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control text-right",
            },
        ),
    )

    deposit_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    account_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class CashbookForm(forms.Form):
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "placeholder": _("YYYY-MM-DD"),
            },
        ),
    )

    end = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "placeholder": _("YYYY-MM-DD"),
            },
        ),
    )

    update = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control text-right",
            },
        ),
    )

    comment = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": capfirst(_("optional comment")),
            },
        ),
    )


class ShiftsForm(forms.Form):
    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["semester"].choices = choices

    semester = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                "class": "custom-select",
            },
        ),
    )
