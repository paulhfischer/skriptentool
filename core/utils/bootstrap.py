from contextlib import suppress

from django.contrib.messages import get_messages
from django.core.exceptions import ImproperlyConfigured
from django.forms import BaseFormSet
from django.forms import CheckboxInput
from django.forms import EmailInput
from django.forms import FileInput
from django.forms import NumberInput
from django.forms import PasswordInput
from django.forms import Select
from django.forms import TextInput
from django.forms import URLInput
from django.utils.encoding import force_str
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


def text_value(value):
    if value:
        return force_str(value)
    else:
        return ""


def nonfield_errors_renderer(form):
    if form.non_field_errors():
        errors = ""
        for error in form.non_field_errors():
            errors += f"<li>{conditional_escape(text_value(error))}</li>"

        html = (
            '<div class="alert alert-dismissible alert-danger mb-0">'
            '<button type="button" class="close" data-dismiss="alert">'
            '<i class="fa fa-times"></i>'
            "</button>"
            '<ul class="mb-0">'
            f"{errors}"
            "</ul>"
            "</div>"
        )

        return mark_safe(html)  # nosec

    return None


def formset_errors_renderer(formset, model_name):
    if not isinstance(formset, BaseFormSet):
        raise ImproperlyConfigured("no formset provided")

    if formset.non_form_errors():
        alert_class = " alert-danger"
        html = ""
        for error in formset.non_form_errors():
            html += f"<li>{error}</li>"
        html = f"<ul>{html}</ul>"
    elif formset.total_error_count():
        alert_class = " alert-danger"
        html = _("Please correct the marked fields.")
    elif formset.is_valid():
        if formset.has_changed():
            alert_class = " alert-success"
            html = capfirst(_("%(model_name)s successfully saved.") % {"model_name": model_name})
        else:
            alert_class = " alert-secondary"
            html = _("Nothing saved, as no changes have been made.")
    else:
        return None

    html = (
        f'<div class="alert alert-dismissible{alert_class}">'
        '<button type="button" class="close" data-dismiss="alert">'
        '<i class="fa fa-times"></i>'
        "</button>"
        f"{html}"
        "</div>"
    )

    return mark_safe(html)  # nosec


def field_renderer(field, style="default"):
    widget = field.field.widget

    # check if style is supported
    if style not in ["default", "horizontal", "tabular"]:
        raise ImproperlyConfigured()

    # do not render hidden fields
    if field.is_hidden:
        return text_value(field)

    # check if field-type is supported
    if (
        not isinstance(
            widget,
            (
                CheckboxInput,
                FileInput,
                Select,
                TextInput,
                NumberInput,
                EmailInput,
                URLInput,
                PasswordInput,
            ),
        )
        or (style == "tabular" and isinstance(field.field.widget, FileInput))
    ):
        raise ImproperlyConfigured()

    # render errors
    if field.errors:
        validation = " is-invalid"
        invalid_feedback = ""
        for error in field.errors:
            invalid_feedback += (
                f'<div class="invalid-feedback">{conditional_escape(text_value(error))}</div>'
            )
    else:
        validation = ""
        invalid_feedback = ""

    # render wrapper style
    if widget.attrs.get("wrapper_style"):
        wrapper_style = f' style="{"; ".join(widget.attrs.get("wrapper_style"))}"'
    else:
        wrapper_style = ""
    with suppress(KeyError):
        del widget.attrs["wrapper_style"]

    # remove borders if tabular
    border = " border-0" if style == "tabular" else ""

    # bold label if field is required
    required = " font-weight-bold" if field.field.required else ""

    # align numbers right if tabular
    align_right = " text-right" if isinstance(widget, NumberInput) and style == "tabular" else ""

    # add class to disable checkbox
    disabled_css = " disabled" if isinstance(widget, CheckboxInput) and field.field.disabled else ""

    # small inputs if tabular
    if style == "tabular":
        small = " custom-select-sm" if isinstance(widget, Select) else " form-control-sm"
    else:
        small = ""

    # modify widget
    if isinstance(widget, CheckboxInput):
        widget.attrs["class"] = "custom-control-input"

    elif isinstance(widget, FileInput):
        widget.attrs["class"] = "custom-file-input"

    elif isinstance(widget, Select):
        widget.attrs["class"] = f"custom-select {small}{border}{validation}"

    else:
        widget.attrs["class"] = f"form-control {small}{border}{align_right}{validation}"

        # set placeholder if field is not disabled
        if not field.field.disabled:
            widget.attrs["placeholder"] = widget.attrs.get("placeholder", text_value(field.label))

    # modify input-types
    # currently disabled, as django does not return rfc3339-formatted date for inputs
    # if isinstance(field.field, DateTimeField):
    #     setattr(widget, 'input_type', 'datetime-local')

    # generate html for field
    input_html = field.as_widget(attrs=widget.attrs)

    # render wrapper with field
    if isinstance(widget, CheckboxInput):
        if style == "default":
            html = (
                f'<div class="form-group {validation}">'
                '<div class="custom-control custom-switch">'
                f"{input_html}"
                f'<label class="custom-control-label{disabled_css}" for="{field.id_for_label}">'
                f"{text_value(field.label)}"
                "</label>"
                "</div>"
                "</div>"
            )
        elif style == "horizontal":
            html = (
                f'<div class="form-group row{validation}">'
                '<label class="col-md-3 col-form-label"></label>'
                '<div class="col-md-9 d-flex align-items-center">'
                '<div class="custom-control custom-switch">'
                f"{input_html}"
                f'<label class="custom-control-label{disabled_css}" for="{field.id_for_label}">'
                f"{text_value(field.label)}"
                "</label>"
                "</div>"
                "</div>"
                "</div>"
            )
        else:
            html = (
                f'<td class="align-middle text-center{validation}"{wrapper_style}>'
                '<div class="custom-control custom-switch">'
                f"{input_html}"
                f'<label class="custom-control-label{disabled_css}" for="{field.id_for_label}">'
                "</label>"
                "</div>"
                "</td>"
            )

    elif isinstance(widget, FileInput):
        if style == "default":
            html = (
                f'<div class="form-group {required}">'
                f'<label for="{field.id_for_label}">{text_value(field.label)}</label>'
                '<div class="custom-file">'
                f'<input type="file" name="{field.name}" class="custom-file-input" '
                f'id="{field.id_for_label}">'
                f'<label class="custom-file-label" for="{field.id_for_label}">'
                f"{text_value(field.value())}"
                "</label>"
                f"{invalid_feedback}"
                "</div>"
                "</div>"
            )
        else:
            html = (
                f'<div class="form-group row {required}">'
                f'<label class="col-md-3 col-form-label" for="{field.id_for_label}">'
                f"{text_value(field.label)}"
                "</label>"
                '<div class="col-md-9 my-auto">'
                '<div class="custom-file">'
                f'<input type="file" name="{field.name}" class="custom-file-input" '
                f'id="{field.id_for_label}">'
                f'<label class="custom-file-label" for="{field.id_for_label}">'
                f'{text_value(field.value()).replace("media/", "")}'
                "</label>"
                f"{invalid_feedback}"
                "</div>"
                "</div>"
                "</div>"
            )

    else:
        if style == "default":
            html = (
                f'<div class="form-group {required}">'
                f'<label for="{field.id_for_label}">{text_value(field.label)}</label>'
                f"{input_html}"
                f"{invalid_feedback}"
                "</div>"
            )
        elif style == "horizontal":
            html = (
                f'<div class="form-group row {required}">'
                f'<label class="col-md-3 col-form-label" for="{field.id_for_label}">'
                f"{text_value(field.label)}"
                "</label>"
                '<div class="col-md-9 my-auto">'
                f"{input_html}"
                f"{invalid_feedback}"
                "</div>"
                "</div>"
            )
        else:
            html = f'<td class="p-0"{wrapper_style}>{input_html}</td>'

    return mark_safe(html)  # nosec


def messages_renderer(context):
    html = ""
    for message in get_messages(context.request):
        html += (
            f'<div class="alert alert-dismissible alert-{message.tags}">'
            '<button type="button" class="close" data-dismiss="alert">'
            '<i class="fa fa-times"></i>'
            "</button>"
            f"{message}"
            "</div>"
        )

    return mark_safe(html)  # nosec
