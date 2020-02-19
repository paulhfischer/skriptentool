from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path('', views.catalogue, name="catalogue"),
    path('verkauf/', views.sale, name="sale"),
    path('finanz/', views.finance, name="finance"),
]
