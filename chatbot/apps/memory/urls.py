from django.urls import path
from . import views

urlpatterns = [
    path("", views.memory_list, name="memory_list"),
    path("<uuid:pk>/", views.memory_detail, name="memory_detail"),
]