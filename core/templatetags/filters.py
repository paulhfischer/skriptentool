from django import template

from core.models import User

register = template.Library()


# split string with "|" as seperator
@register.filter(name="split")
def split(string, position):
    return string.split("|")[int(position)]


# get username from user-id
@register.filter(name="username_from_id")
def username_from_id(uid):
    return User.objects.get(id=uid).username


# check if variable is string
@register.filter(name="is_string")
def is_string(var):
    return isinstance(var, str)


# check if variable is tuple
@register.filter(name="is_tuple")
def is_tuple(var):
    return isinstance(var, tuple)
