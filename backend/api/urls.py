from django.urls import path
from .views import language_data, add_availability

urlpatterns = [
    path('<str:language>/', language_data),
    path('<str:language>/add-availability/', add_availability),
]