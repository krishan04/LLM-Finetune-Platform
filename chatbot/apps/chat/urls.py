from django.urls import path
from . import views

urlpatterns = [
    path("conversations/", views.conversation_list, name="conversation_list"),
    path("conversations/<uuid:pk>/", views.conversation_detail, name="conversation_detail"),
    path("conversations/<uuid:pk>/messages/", views.message_list, name="message_list"),
]