from django.db.models import ProtectedError
from django.http import Http404
from django.urls import reverse
from django.views.generic import DeleteView

from core.utils.functions import get_model
from core.utils.management import is_allowed


def get_context(user, model):
    return {
        "verbose_name": model._meta.verbose_name,
        "abort_url": reverse("core:management_list", args=[model.__name__.lower()]),
    }


class DeleteModelView(DeleteView):
    template_name = "core/management/delete_model.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request.user, get_model(self.kwargs["model"])))
        return context

    def get_success_url(self):
        return reverse("core:management_list", args=[self.kwargs["model"]])

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError:
            context = self.get_context_data(**kwargs)
            context["error"] = True
            return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])

        if not is_allowed(request.user, self.model, "delete"):
            raise Http404

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = get_model(kwargs["model"])

        if not is_allowed(request.user, self.model, "delete"):
            raise Http404

        return super().post(request, *args, **kwargs)
