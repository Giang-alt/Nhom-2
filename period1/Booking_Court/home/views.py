from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import CourtNewForm

# Create your views here.

def home(request):
    return render(request, 'home.html')

def edit_court(request, id=None):
    template = loader.get_template('app_home/court/edit-court.html')
    context = {
        'court' : courts,
    }
    return HttpResponse(template.render(context, request))

def courts(request):
    template = loader.get_template('app_home/court/courts.html')
    context = {
        'court' : courts, #thieu data
    }
    return HttpResponse(template.render(context, request))

def new_court(request):
    if request.method == "POST":
        form = CourtNewForm(request.POST)
        print(form)
        if form. is_valid():
            pass
            return HttpResponseRedirect("/courts")

    template = loader.get_template('app_home/court/new-court.html')
    context = {
        
    }
    return HttpResponse(template.render(context, request))
