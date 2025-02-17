"""
URLS for movietrendapp
"""

from django.urls import path
from .views import get_integration_json, telex_tick

app_name = "movietrendapp"

urlpatterns = [
    path("telex-integration/", get_integration_json, name="telex_integration"),
    path("tick/", telex_tick, name="telex_tick"),
]
