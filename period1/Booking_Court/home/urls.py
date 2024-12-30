from django.contrib import admin
from django.urls import include, path
from .import views
urlpatterns = [
    path('', views.home, name = "home"),
     path('court-manage/', views.court_manage, name='court_manage'),
    path('court-types/edit/', views.edit_court_manager, name='edit_court_manager'),
]

