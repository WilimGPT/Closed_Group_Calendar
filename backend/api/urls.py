from django.urls import path
from .views import language_data

urlpatterns = [
    path('<str:language>/', language_data),
]