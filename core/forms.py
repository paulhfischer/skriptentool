from django import forms


class SaleForm(forms.Form):
    ean_add = forms.IntegerField(label = "Artikel hinzufügen", required = False, widget = forms.NumberInput(
        attrs = {"class": "form-control", "style": "text-align: left;", "autofocus": ""}))
    ean_remove = forms.IntegerField(label = "Artikel entfernen", required = False, widget = forms.NumberInput(
        attrs = {"class": "form-control", "style": "text-align: left;"}))
    balance = forms.DecimalField(max_digits = 6, decimal_places = 2, required = False, widget = forms.NumberInput(
        attrs = {"class": "form-control", "style": "text-align: right;"}))
    deposit = forms.IntegerField(required = False, widget = forms.NumberInput(attrs = {"class": "form-control"}))


class CashbookForm(forms.Form):
    start = forms.DateField(required = False, widget = forms.DateInput(attrs = {"class": "form-control"}))
    end = forms.DateField(required = False, widget = forms.DateInput(attrs = {"class": "form-control"}))
    update = forms.DecimalField(max_digits = 6, decimal_places = 2, required = False, widget = forms.NumberInput(
        attrs = {"class": "form-control", "style": "text-align: right;"}))
