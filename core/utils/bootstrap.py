from django.core.exceptions import ImproperlyConfigured
from django.forms import BaseFormSet, CheckboxInput, DateTimeField, EmailInput, FileInput, NumberInput, PasswordInput, Select, TextInput, URLInput
from django.utils.encoding import force_str
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def text_value(value):
    if value:
        return force_str(value)
    else:
        return ''


def nonfield_errors_renderer(form):
    if form.non_field_errors():
        errors = ''
        for error in form.non_field_errors():
            errors += '<li>{}</li>'.format(conditional_escape(text_value(error)))

        html = '<div class="alert alert-dismissible alert-danger mb-0">' \
               '<button type="button" class="close" data-dismiss="alert"><i class="fa fa-times"></i></button>' \
               '<ul class="mb-0">' \
               '{}' \
               '</ul>' \
               '</div>' \
               .format(errors)

        return mark_safe(html)


def formset_errors_renderer(formset, model_name):
    if not isinstance(formset, BaseFormSet):
        raise ImproperlyConfigured('no formset provided')

    if formset.non_form_errors():
        alert_class = ' alert-danger'
        html = ''
        for error in formset.non_form_errors():
            html += '<li>{}</li>'.format(error)
        html = '<ul>{}</ul>'.format(html)
    elif formset.total_error_count():
        alert_class = ' alert-danger'
        html = _('Please correct the marked fields.')
    elif formset.is_valid():
        if formset.has_changed():
            alert_class = ' alert-success'
            html = _('%(model_name)s successfully saved.') % {'model_name': model_name}
        else:
            alert_class = ' alert-dark'
            html = _('Nothing saved, as no changes have been made.')
    else:
        return ''

    html = '<div class="alert alert-dismissible{}">' \
           '<button type="button" class="close" data-dismiss="alert"><i class="fa fa-times"></i></button>' \
           '{}' \
           '</div>' \
           .format(alert_class, html)

    return mark_safe(html)


def field_renderer(field, style='default'):
    widget = field.field.widget

    # check if style is supported
    if style not in ['default', 'horizontal', 'tabular']:
        raise ImproperlyConfigured()

    # do not render hidden fields
    if field.is_hidden:
        return text_value(field)

    # check if field-type is supported
    if not isinstance(
            widget, (CheckboxInput, FileInput, Select, TextInput, NumberInput, EmailInput, URLInput, PasswordInput,)
       ) or (
            style == 'tabular' and isinstance(field.field.widget, FileInput)
       ):
        raise ImproperlyConfigured()

    # render errors
    if field.errors:
        validation = ' is-invalid'
        invalid_feedback = ''
        for error in field.errors:
            invalid_feedback += '<div class="invalid-feedback">{}</div>'.format(conditional_escape(text_value(error)))
    else:
        validation = ''
        invalid_feedback = ''

    # remove borders if tabular
    border = ' border-0' if style == 'tabular' else ''

    # bold label if field is required
    required = ' font-weight-bold' if field.field.required else ''

    # align numbers right if tabular
    align_right = ' text-right' if isinstance(widget, NumberInput) and style == 'tabular' else ''

    # add class to disable checkbox
    disabled_css = ' disabled' if isinstance(widget, CheckboxInput) and field.field.disabled else ''

    # small inputs if tabular
    if style == 'tabular':
        small = ' custom-select-sm' if isinstance(widget, Select) else ' form-control-sm'
    else:
        small = ''

    # modify widget
    if isinstance(widget, CheckboxInput):
        widget.attrs['class'] = 'custom-control-input'

    elif isinstance(widget, FileInput):
        widget.attrs['class'] = 'custom-file-input'

    elif isinstance(widget, Select):
        widget.attrs['class'] = 'custom-select {}{}{}'.format(small, border, validation)

    else:
        widget.attrs['class'] = 'form-control {}{}{}{}'.format(small, border, align_right, validation)

        # set placeholder if field is not disabled
        if not field.field.disabled:
            widget.attrs['placeholder'] = widget.attrs.get('placeholder', text_value(field.label))

    # modify input-types
    if isinstance(field.field, DateTimeField):
        setattr(widget, 'input_type', 'datetime-local')

    # generate html for field
    input_html = field.as_widget(attrs=widget.attrs)

    # render wrapper with field
    if isinstance(widget, CheckboxInput):
        if style == 'default':
            html = '<div class="form-group {validation}">' \
                   '<div class="custom-control custom-switch">' \
                   '{input}' \
                   '<label class="custom-control-label{disabled_css}" for="{input_id}">{label_content}</label>' \
                   '</div>' \
                   '</div>' \
                   .format(
                       validation=validation,
                       input_id=field.id_for_label,
                       input=input_html,
                       label_content=text_value(field.label),
                       disabled_css=disabled_css,
                   )
        elif style == 'horizontal':
            html = '<div class="form-group row{validation}">' \
                   '<label class="col-md-3 col-form-label"></label>' \
                   '<div class="col-md-9 d-flex align-items-center">' \
                   '<div class="custom-control custom-switch">' \
                   '{input}' \
                   '<label class="custom-control-label{disabled_css}" for="{input_id}">{label_content}</label>' \
                   '</div>' \
                   '</div>' \
                   '</div>' \
                   .format(
                       validation=validation,
                       input_id=field.id_for_label,
                       input=input_html,
                       label_content=text_value(field.label),
                       disabled_css=disabled_css,
                   )
        else:
            html = '<td class="align-middle text-center{validation}">' \
                   '<div class="custom-control custom-switch">' \
                   '{input}' \
                   '<label class="custom-control-label{disabled_css}" for="{input_id}"></label>' \
                   '</div>' \
                   '</td>' \
                   .format(
                       validation=validation,
                       input_id=field.id_for_label,
                       input=input_html,
                       disabled_css=disabled_css,
                   )

    elif isinstance(widget, FileInput):
        if style == 'default':
            html = '<div class="form-group {required}">' \
                   '<label for="{input_id}">{label_content}</label>' \
                   '<div class="custom-file">' \
                   '<input type="file" name="{input_name}" class="custom-file-input" id="{input_id}">' \
                   '<label class="custom-file-label" for="{input_id}">{value}</label>' \
                   '{invalid_feedback}' \
                   '</div>' \
                   '</div>' \
                   .format(
                       invalid_feedback=invalid_feedback,
                       value=text_value(field.value()),
                       input_name=field.name,
                       input_id=field.id_for_label,
                       label_content=text_value(field.label),
                       required=required,
                   )
        else:
            html = '<div class="form-group row {required}">' \
                   '<label class="col-md-3 col-form-label" for="{input_id}">{label_content}</label>' \
                   '<div class="col-md-9 my-auto">' \
                   '<div class="custom-file">' \
                   '<input type="file" name="{input_name}" class="custom-file-input" id="{input_id}">' \
                   '<label class="custom-file-label" for="{input_id}">{value}</label>' \
                   '{invalid_feedback}' \
                   '</div>' \
                   '</div>' \
                   '</div>' \
                   .format(
                       invalid_feedback=invalid_feedback,
                       value=text_value(field.value()).replace('media/', ''),
                       input_name=field.name,
                       input_id=field.id_for_label,
                       label_content=text_value(field.label),
                       required=required,
                   )

    else:
        if style == 'default':
            html = '<div class="form-group {required}">' \
                   '<label for="{input_id}">{label_content}</label>' \
                   '{input}' \
                   '{invalid_feedback}' \
                   '</div>' \
                   .format(
                       invalid_feedback=invalid_feedback,
                       input_id=field.id_for_label,
                       input=input_html,
                       label_content=text_value(field.label),
                       required=required
                   )
        elif style == 'horizontal':
            html = '<div class="form-group row {required}">' \
                   '<label class="col-md-3 col-form-label" for="{input_id}">{label_content}</label>' \
                   '<div class="col-md-9 my-auto">' \
                   '{input}' \
                   '{invalid_feedback}' \
                   '</div>' \
                   '</div>' \
                   .format(
                       invalid_feedback=invalid_feedback,
                       input_id=field.id_for_label,
                       input=input_html,
                       label_content=text_value(field.label),
                       required=required,
                   )
        else:
            html = '<td class="p-0">' \
                   '{input}' \
                   '</td>' \
                   .format(
                       input=input_html
                   )

    return mark_safe(html)
