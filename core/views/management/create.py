from django import forms
from django.contrib import messages
from django.contrib.auth import password_validation
from django.forms import ModelForm
from django.forms import ValidationError
from django.http import Http404
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from core.models import User
from core.utils.functions import get_model
from core.utils.management import get_fields
from core.utils.management import get_fieldsets
from core.utils.management import is_allowed


def get_context(user, model):
    return {
        "verbose_name": model._meta.verbose_name,
        "mode": "create",
        "abort_url": reverse("core:management_list", args=[model.__name__.lower()]),
        "fieldsets": get_fieldsets(user, model),
    }


def get_form(form_model, user):
    if form_model != User:

        class CreateModelForm(ModelForm):
            class Meta:
                model = form_model
                fields = get_fields(user, form_model, "create")

    else:
        # special form for user creation
        class CreateModelForm(ModelForm):
            class Meta:
                model = User
                fields = get_fields(user, User, "create")

            password = forms.CharField(
                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
                label=_("password"),
            )

            password_repeat = forms.CharField(
                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
                label=_("repeat password"),
            )

            def clean_password_repeat(self):
                password = self.cleaned_data.get("password")
                password_repeat = self.cleaned_data.get("password_repeat")

                if password and password_repeat and password != password_repeat:
                    raise ValidationError(_("The passwords don't match."))

                return password_repeat

            def _post_clean(self):
                super()._post_clean()

                password = self.cleaned_data.get("password_repeat")
                if password:
                    try:
                        password_validation.validate_password(password, self.instance)
                    except forms.ValidationError as error:
                        self.add_error("password_repeat", error)

            def save(self, commit=True):
                new_user = super().save(commit=False)
                new_user.set_password(self.cleaned_data["password"])
                if commit:
                    new_user.save()
                return new_user

    return CreateModelForm


class CreateModelView(CreateView):
    template_name = "core/management/update_model.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request.user, get_model(self.kwargs["model"])))
        return context

    def get_success_url(self):
        messages.success(
            self.request,
            capfirst(
                _("<strong>%(object_name)s</strong> successfully created.")
                % {"object_name": self.object},
            ),
        )
        return reverse("core:management_list", args=[self.kwargs["model"]])

    def get_form_class(self):
        return get_form(get_model(self.kwargs.get("model")), self.request.user)

    def get(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])

        if not is_allowed(request.user, self.model, "create"):
            raise Http404

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])
        self.form_class = get_form(self.model, request.user)

        if not is_allowed(request.user, self.model, "create"):
            raise Http404

        return super().post(request, *args, **kwargs)
