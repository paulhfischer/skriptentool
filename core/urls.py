from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path('', views.catalogue, name="catalogue"),
    path('sale/', views.sale, name="sale"),
    path('finance/', views.finance, name="finance"),
    path('shifts/', views.shifts, name="shifts"),
]
