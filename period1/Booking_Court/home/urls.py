from django.contrib import admin
from django.urls import include, path
from .import views
urlpatterns = [
    path('', views.home, name = "home"),
    path ('courts', views.courts, name = "courts"),
    path ('edit-court', views.edit_court, name = "edit-court"),
    path ('new-court', views.new_court, name = "new-court"),
    path ('delete-court', views.delete_court, name = "delete_court"),
]

