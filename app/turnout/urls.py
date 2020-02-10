from django.contrib import admin
from django.urls import include, path

from .api_routes import router

urlpatterns = [
    path("-/", include("django_alive.urls")),
    path("v1/", include(router.urls)),
    path("manage/admin/", admin.site.urls),
    path("manage/", include("manage.urls", namespace="manage")),
    path("account/", include("accounts.urls", namespace="accounts")),
]
