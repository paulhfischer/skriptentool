from django import template

from core.utils.bootstrap import field_renderer
from core.utils.bootstrap import formset_errors_renderer
from core.utils.bootstrap import nonfield_errors_renderer

register = template.Library()


@register.simple_tag()
def bootstrap_formseterrors(formset, model_name):
    return formset_errors_renderer(formset, model_name)


@register.simple_tag()
def bootstrap_tablefield(field):
    return field_renderer(field, "tabular")


@register.simple_tag()
def bootstrap_horizontalfield(field):
    return field_renderer(field, "horizontal")


@register.simple_tag()
def bootstrap_listfield(field):
    return field_renderer(field)


@register.simple_tag()
def bootstrap_nonfielderrors(field):
    return nonfield_errors_renderer(field)
