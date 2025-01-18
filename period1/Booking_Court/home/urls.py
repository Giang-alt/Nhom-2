from django.contrib import admin
from django.urls import include, path
from .import views
urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.user_interface, name = "user-interface"),
    path ('courts/', views.courts, name = "courts"),
    path('edit-court/<int:id>/', views.edit_court, name='edit-court'),
    path ('new-court', views.new_court, name = "new-court"),
    path('delete-court/', views.delete_court, name='delete_court'),
    path('login/', views.login_view, name='login'),  
    path('register/', views.register, name='register'),  
    path('account/', views.account_view, name='account'),

]