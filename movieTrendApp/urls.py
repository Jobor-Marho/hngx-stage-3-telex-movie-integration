"""
URLS for movietrendapp
"""
from django.urls import path
from django.shortcuts import redirect
from .views import get_integration_json, telex_tick

app_name = "movietrendapp"

urlpatterns = [
    # Redirect root path to external website (the Movie Database)
    path("", lambda request: redirect("https://www.themoviedb.org")),  # Root path redirect

    # Integration JSON for Telex
    path("integration.json", get_integration_json, name="telex_integration"),

    # Telex tick endpoint to fetch and send trending movies
    path("tick", telex_tick, name="telex_tick"),
]
