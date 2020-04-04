from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.unregister(Group)

for model in apps.get_app_config("core").get_models():
    admin.site.register(model)
