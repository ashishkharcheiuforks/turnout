from django.urls import path

from storage import api_views

app_name = "storage_api"
urlpatterns = [
    path("download/", api_views.DownloadView.as_view(), name="download"),
    path("reset/", api_views.ResetView.as_view(), name="reset"),
]
