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
    court = get_object_or_404(Court, id=id)

    if request.method == 'POST':
        form = CourtNewForm(request.POST, instance=court)
        if form.is_valid():
            form.save()
            court.update_active_status()  # Cập nhật trạng thái sau khi lưu
            return redirect('courts')  
        else:
            print(form.errors)
    else:
        form = CourtNewForm(instance=court)
    return render(request, 'app_home/court/edit-court.html', {'form': form, 'court': court})

def courts(request):
    courts_data = Court.objects.all() 
    # Cập nhật trạng thái Active cho mỗi sân
    for court in courts_data:
        court.update_active_status()  # Cập nhật trạng thái của mỗi sân 
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
        court_id = request.POST.get('court_id')  
        court = get_object_or_404(Court, id=court_id)
        court.delete() 
        return redirect('courts')  

    return redirect('courts')  