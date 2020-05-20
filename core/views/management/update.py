from django.contrib import messages
from django.forms import ModelForm
from django.http import Http404
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from core.models import User
from core.utils.functions import get_model
from core.utils.management import get_disabled_fields
from core.utils.management import get_fields
from core.utils.management import get_fieldsets
from core.utils.management import is_allowed


def get_context(user, model, pk):
    return {
        "verbose_name": model._meta.verbose_name,
        "mode": "update",
        "abort_url": reverse("core:management_list", args=[model.__name__.lower()]),
        "delete_url": reverse("core:management_delete", args=[model.__name__.lower(), pk])
        if is_allowed(user, model, "delete")
        else None,
        "fieldsets": get_fieldsets(user, model),
    }


def get_form(user, form_model):
    if form_model != User:

        class UpdateModelForm(ModelForm):
            class Meta:
                model = form_model
                fields = get_fields(user, form_model, "list")

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for field in self.fields:
                    if field in get_disabled_fields(user, form_model, "update"):
                        self.fields[field].disabled = True
                        self.fields[field].required = False

    else:
        # special form for user update
        class UpdateModelForm(ModelForm):
            class Meta:
                model = User
                fields = [
                    field
                    for field in get_fields(user, User, "list")
                    if field not in ["password", "password_repeat"]
                ]

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                # enable update of local user for admins
                if not (self.initial.get("username").startswith("@") and user.admin):
                    for field in self.fields:
                        if field in get_disabled_fields(user, form_model, "update"):
                            self.fields[field].disabled = True
                            self.fields[field].required = False

            def clean(self):
                super().clean()

                # skip username-validation for non-local user
                if self.fields["username"].disabled:
                    del self.cleaned_data["username"]
                return self.cleaned_data

    return UpdateModelForm


class UpdateModelView(UpdateView):
    template_name = "core/management/update_model.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update(
            get_context(self.request.user, get_model(self.kwargs["model"]), self.kwargs["pk"]),
        )
        return context

    def form_valid(self, form):
        if form.has_changed():
            messages.success(
                self.request,
                capfirst(
                    _("<strong>%(object_name)s</strong> successfully saved.")
                    % {"object_name": self.object},
                ),
            )
        else:
            messages.info(
                self.request,
                _("Nothing saved, as no changes have been made."),
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:management_list", args=[self.kwargs["model"]])

    def get_form_class(self):
        return get_form(self.request.user, get_model(self.kwargs["model"]))

    def get(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])

        if not is_allowed(request.user, self.model, "update"):
            raise Http404

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])

        if not is_allowed(request.user, self.model, "update"):
            raise Http404

        self.form_class = get_form(request.user, self.model)
        return super().post(request, *args, **kwargs)
