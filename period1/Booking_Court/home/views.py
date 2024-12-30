from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request, 'home\home.html')



def edit_court_manager(request, id=None):
    return render(request, 'home/edit_court_manager.html')

def court_manage(request):
    return render(request, 'home/court_manage.html')