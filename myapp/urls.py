from django.urls import path
from .import views

urlpatterns = [
    path('', views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),
]


# es not appear to have any patterns in it. If you see the 'urlpatterns' variable with valid patterns in the file then the issue is probably caused by a circular import.


