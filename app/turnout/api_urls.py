from django.urls import include, path

app_name = "api"
urlpatterns = [
    path("registration/", include("register.api_urls")),
    path("verification/", include("verifier.api_urls")),
    path("election/", include("election.api_urls")),
]
