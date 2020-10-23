from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.forms import BaseModelFormSet
from django.forms import ModelForm
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.models import User
from core.utils.functions import get_model
from core.utils.management import get_column_style
from core.utils.management import get_columns
from core.utils.management import get_disabled_columns
from core.utils.management import is_allowed


def get_context(user, model):
    return {
        "verbose_name": model._meta.verbose_name,
        "verbose_name_plural": model._meta.verbose_name_plural,
        "model_name": model.__name__.lower(),
        "create_url": reverse("core:management_create", args=[model.__name__.lower()]),
        "can_update": is_allowed(user, model, "update"),
        "can_delete": is_allowed(user, model, "delete"),
        "can_create": is_allowed(user, model, "create"),
        "editable_fields": len(get_columns(user, model)) != len(get_disabled_columns(user, model)),
        "ordering": model._meta.ordering,
    }


def get_formset(user, form_model):
    if form_model != User:

        class ListModelForm(ModelForm):
            class Meta:
                model = form_model
                fields = get_columns(user, form_model)

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for field in self.fields:
                    if field in get_disabled_columns(user, form_model):
                        self.fields[field].disabled = True
                        self.fields[field].required = False
                    self.fields[field].widget.attrs["wrapper_style"] = get_column_style(
                        form_model,
                        field,
                    )

    else:
        # special form for user update
        class ListModelForm(ModelForm):
            class Meta:
                model = User
                fields = [
                    field
                    for field in get_columns(user, User)
                    if field not in ["password", "password_repeat"]
                ]

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                # enable update of local user for admins
                if not (self.initial.get("username").startswith("@") and user.admin):
                    for field in self.fields:
                        if field in get_disabled_columns(user, form_model):
                            self.fields[field].disabled = True
                            self.fields[field].required = False

            def clean(self):
                super().clean()

                # skip username-validation for non-local user
                if not self.initial.get("username").startswith("@"):
                    del self.cleaned_data["username"]
                return self.cleaned_data

    class ListModelFormSet(BaseModelFormSet):
        def get_queryset(self):
            return super().get_queryset()

    return modelformset_factory(form_model, ListModelForm, extra=0, formset=ListModelFormSet)


def get_pagination(formset, request):
    query = formset.get_queryset()
    paginator = Paginator(query, 25)

    try:
        page = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(1)

    return query.filter(pk__in=[obj.pk for obj in page]), page


class ListModelView(View):
    def get(self, request, model):
        model = get_model(model)

        if not is_allowed(request.user, model, "list"):
            raise Http404

        context = get_context(request.user, model)

        query, page = get_pagination(get_formset(request.user, model)(), request)

        formset = get_formset(request.user, model)(queryset=query)

        context["page"] = page
        context["formset"] = formset

        return render(request, "core/management/list_model.html", context)

    def post(self, request, model):
        model = get_model(model)

        if not is_allowed(request.user, model, "list"):
            raise Http404

        context = get_context(request.user, model)

        query, page = get_pagination(get_formset(request.user, model)(), request)

        if "save" in request.POST:
            formset = get_formset(request.user, model)(request.POST, queryset=query)
            if formset.is_valid():
                formset.save()
        else:
            formset = get_formset(request.user, model)(queryset=query)

        context["page"] = page
        context["formset"] = formset

        return render(request, "core/management/list_model.html", context)
