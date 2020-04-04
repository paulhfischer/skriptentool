from django.urls import path

from core import views
from core.views import CreateModelView
from core.views import DeleteModelView
from core.views import ListModelView
from core.views import UpdateModelView

app_name = "core"

urlpatterns = [
    path(
        "",
        views.catalogue,
        name="catalogue",
    ),
    path(
        "sale/",
        views.sale,
        name="sale",
    ),
    path(
        "shifts/",
        views.shifts,
        name="shifts",
    ),
    path(
        "management/finance/",
        views.finance,
        name="management_finance",
    ),
    path(
        "management/<str:model>/",
        ListModelView.as_view(),
        name="management_list",
    ),
    path(
        "management/<str:model>/create/",
        CreateModelView.as_view(),
        name="management_create",
    ),
    path(
        "management/<str:model>/<int:pk>/update/",
        UpdateModelView.as_view(),
        name="management_update",
    ),
    path(
        "management/<str:model>/<int:pk>/delete/",
        DeleteModelView.as_view(),
        name="management_delete",
    ),
]
