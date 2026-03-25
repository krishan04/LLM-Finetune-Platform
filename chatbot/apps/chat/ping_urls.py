from django.urls import path
from .ping_views import ping

urlpatterns = [
    path("", ping, name="ping"),
]