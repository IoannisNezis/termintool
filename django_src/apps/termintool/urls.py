from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="hello"),
    path('booking', create_booking, name='book'),
    path('canceling', cancel_booking, name='cancel')
]
