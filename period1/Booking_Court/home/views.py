from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from .forms import CourtNewForm
from django.shortcuts import render, get_object_or_404, redirect
from B_Court_Mng.models import Court

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
    courts_data = Court.objects.all()  
    context = {
        'courts': courts_data, 
    }
    return render(request, 'app_home/court/courts.html', context)
def new_court(request):
    if request.method == "POST":
        form = CourtNewForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('/courts')  
    else:
        form = CourtNewForm()

    return render(request, 'app_home/court/new-court.html', {'form': form})

def delete_court(request):
    if request.method == "POST":
        court_id = request.POST.get("court_id")
        if court_id:
            try:
                court = Court.objects.get(id=court_id)  
                court.delete()  
                return redirect('courts')  
            except Court.DoesNotExist:
                
                return HttpResponse("Không tìm thấy sân", status=404)

    courts_list = Court.objects.all()  
    return render(request, 'app_home/court/delete-court.html', {'courts': courts_list})