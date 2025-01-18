from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from .forms import CourtNewForm
from django.shortcuts import render, get_object_or_404, redirect
from B_Court_Mng.models import Court
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

def home(request):
    courts = Court.objects.all()
    return render(request, 'home.html', {'courts': courts})


def edit_court(request, id=None):
    court = get_object_or_404(Court, id=id)

    if request.method == 'POST':
        form = CourtNewForm(request.POST, instance=court)
        if form.is_valid():
            form.save()
            court.update_active_status()  
            return redirect('courts')  
        else:
            print(form.errors)
    else:
        form = CourtNewForm(instance=court)
    return render(request, 'app_home/court/edit-court.html', {'form': form, 'court': court})

def courts(request):
    courts_data = Court.objects.all() 
   
    for court in courts_data:
        court.update_active_status() 
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

    
    return render(request, 'app_home/court/new-court.html', {'form': form, 'page_name': 'new_court'})

def delete_court(request):
    if request.method == "POST":
        court_id = request.POST.get('court_id')  
        court = get_object_or_404(Court, id=court_id)
        court.delete() 
        return redirect('courts')  

def user_interface(request):
    courts_data = Court.objects.all()
    for court in courts_data:
        court.update_active_status()   
    context = {
        'courts': courts_data,
    }
    return render(request, 'app_home/user/user-interface.html', context)

def register(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form đăng ký
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms = request.POST.get('terms')

        # Kiểm tra người dùng đồng ý điều khoản
        if terms != 'on':
            messages.error(request, "You must agree to the terms and conditions.")
            return redirect('register')

        # Kiểm tra mật khẩu và mật khẩu xác nhận
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Kiểm tra tên người dùng đã tồn tại hay chưa
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Kiểm tra email đã tồn tại hay chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Tạo người dùng mới
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Thông báo cho người dùng
        messages.success(request, "Registration successful! Please log in to continue.")

        # Chuyển hướng người dùng đến trang đăng nhập
        return redirect('login')  

    context = {
        'title': 'Đăng ký tài khoản',
        'message': 'Chào mừng bạn đến trang đăng ký!',
    }

    return render(request, 'app_home/user/register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Kiểm tra người dùng với username và password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Đăng nhập người dùng
            return redirect('home')  # Chuyển hướng về trang home sau khi đăng nhập
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'app_home/user/login.html')


def account_view(request):
    return render(request, 'app_home/user/account.html')