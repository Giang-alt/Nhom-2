from django.urls import path, include
from . import views

urlpatterns = [
    path('B_Court_Mng/', views.Courts, name='Courts'),
    path('schedules/', views.schedule_list, name='schedule-list'),
    path('schedules/book/<int:court_id>/', views.book_court, name='book-court'),
    path('schedules/edit/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('schedules/delete/<int:id>/', views.delete_schedule, name='delete_schedule'),
    path('schedules/check-conflict/', views.check_schedule_conflict, name='check_schedule_conflict'),
]
