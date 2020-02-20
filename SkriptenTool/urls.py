from django.contrib import admin
from django.urls import include, path

urlpatterns = [path('', include("core.urls")), path('', include("django.contrib.auth.urls")),
               path('admin/', admin.site.urls), ]
