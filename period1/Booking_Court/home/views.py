from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from .forms import CourtNewForm
from django.shortcuts import render, get_object_or_404, redirect
from B_Court_Mng.models import Court
from B_Court_Mng.models import Booking
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
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
      
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms = request.POST.get('terms')
        role = request.POST.get('role') 

        if terms != 'on':
            messages.error(request, "You must agree to the terms and conditions.")
            return redirect('register')

       
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

   
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

      
        if role == 'Admin':
            group = Group.objects.get(name='Admin')  
        else:
            group = Group.objects.get(name='User')  
        user.groups.add(group)

  
        messages.success(request, "Registration successful! Please log in to continue.")

       
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

       
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) 
            return redirect('home')  
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'app_home/user/login.html')



@login_required
def account_view(request):
    user = request.user  

    if request.method == 'POST':
       
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        confirm_deletion = request.POST.get('confirm_deletion')  

       
        if not first_name or not email:
            messages.error(request, "First Name và Email là bắt buộc!")
            return redirect('account')

       
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại.")
            return redirect('account')

        
        if confirm_deletion:
            
            user.delete()
            messages.success(request, "Tài khoản của bạn đã được xóa.")
            return redirect('http://127.0.0.1:8000/')  

        
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        messages.success(request, "Cập nhật thông tin thành công!")
        return redirect('home')  

    return render(request, 'app_home/user/account.html', {'user': user})



@login_required

def book_court(request):
    if request.method == 'POST':
        # Lấy giá trị court_id từ form
        court_id = request.POST.get('court_id')
        court = Court.objects.get(id=court_id)

        booking_type = request.POST.get('booking_type')
        user = request.user

        if booking_type == 'fixed':
            fixed_day = request.POST.get('fixed_day')
            fixed_time = request.POST.get('fixed_time')
            fixed_months = int(request.POST.get('fixed_months'))
            Booking.objects.create(
                user=request.user,
                court=court,
                booking_type='fixed',
                fixed_day=fixed_day,
                time_slot=fixed_time,
                fixed_months=fixed_months
            )
        elif booking_type == 'daily':
            daily_date = request.POST.get('daily_date')
            daily_time = request.POST.get('daily_time')
            Booking.objects.create(
                user=request.user,
                court=court,
                booking_type='daily',
                booking_date=daily_date,
                time_slot=daily_time
            )
        elif booking_type == 'flexible':
            flexible_hours = int(request.POST.get('flexible_hours'))
            Booking.objects.create(
                user=request.user,
                court=court,
                booking_type='flexible',
                flexible_hours=flexible_hours
            )
        
        messages.success(request, "Court booked successfully!")
        return redirect('book_court')
    else:
        courts = Court.objects.all()
        return render(request, 'app_home/booking/book_court.html', {'courts': courts})

from django.contrib.auth.decorators import login_required, user_passes_test

 #Kiểm tra nếu người dùng là admin
def is_admin(user):
    return user.is_superuser

@login_required
#@user_passes_test(is_admin)
def booking_list(request):
    bookings = Booking.objects.all()  # Lấy tất cả các booking của admin
    return render(request, 'app_home/booking/booking_list.html', {'bookings': bookings})
# Kiểm tra xem user có phải admin không
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def edit_booking(request, booking_id):
    # Lấy thông tin booking từ ID
    booking = get_object_or_404(Booking, id=booking_id)

    # Xử lý dữ liệu khi form được gửi
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated successfully!")
            return redirect('booking_list')  # Quay lại danh sách booking
        else:
            messages.error(request, "There was an error updating the booking.")
    else:
        form = BookingForm(instance=booking)

    # Hiển thị form chỉnh sửa
    return render(request, 'edit_booking.html', {'form': form, 'booking': booking})

@login_required
def check_in(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.check_in_status:
        messages.warning(request, "You have already checked in for this booking.")
    else:
        booking.check_in_status = True
        booking.save()
        messages.success(request, "Check-in successful!")

    return redirect('booking_list')  # Chuyển hướng về danh sách đặt sân