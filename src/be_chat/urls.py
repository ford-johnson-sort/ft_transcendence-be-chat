# mysite/urls.py
from django.urls import include, path

urlpatterns = [
    path("chat/", include("chat.urls")),
]
