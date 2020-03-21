from django import template
from django.contrib.auth.models import User

register = template.Library()


# check if user is in group
@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


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
