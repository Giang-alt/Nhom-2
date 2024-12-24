from django.urls import path
from . import views

urlpatterns = [
    path('B_Court_Mng/', views.Courts, name='Courts'),
]