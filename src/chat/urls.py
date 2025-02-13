# chat/urls.py
from django.urls import path
from .views import new_chat

urlpatterns = [
    path('new/', new_chat, name='new_chat'),
]
