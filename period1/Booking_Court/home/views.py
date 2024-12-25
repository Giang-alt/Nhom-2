from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'home.html')

def courts(request):
    courts = courts.objects.all()
    template = loader.get_template('app-home/courts.html')
    context = {
        'courts': courts,
    }
    return HttpResponse(template.render(context, request))

def edit_court(request):
    court = courts.objects.get(id = 1)
    template = loader.get_template('app-home/edit-court.html') 
    context = {
        'court': court,
    }
    return HttpResponse(template.render(context, request))