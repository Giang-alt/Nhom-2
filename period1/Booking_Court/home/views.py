from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CourtNewForm
from B_Court_Mng.models import Court

# Home page view
def home(request):
    courts = Court.objects.all()
    return render(request, 'home.html', {'courts': courts})

# Edit court details
def edit_court(request, id=None):
    court = get_object_or_404(Court, id=id)

    if request.method == 'POST':
        form = CourtNewForm(request.POST, instance=court)
        if form.is_valid():
            form.save()
            court.update_active_status()  # Update active status after saving
            return redirect('courts')  # Redirect to courts list page
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = CourtNewForm(instance=court)  # Pre-fill form with court's current data
    
    return render(request, 'app_home/court/edit-court.html', {'form': form, 'court': court})

# Courts list page
def courts(request):
    courts_data = Court.objects.all()
    
    # Update active status for each court
    for court in courts_data:
        court.update_active_status()
    
    return render(request, 'app_home/court/courts.html', {'courts': courts_data})

# Create a new court
def new_court(request):
    if request.method == "POST":
        form = CourtNewForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new court
            return redirect('/courts')  # Redirect to courts list page
    else:
        form = CourtNewForm()

    return render(request, 'app_home/court/new-court.html', {'form': form, 'page_name': 'new_court'})

# Delete a court
def delete_court(request):
    if request.method == "POST":
        court_id = request.POST.get('court_id')
        court = get_object_or_404(Court, id=court_id)
        court.delete()  # Delete the court
        return redirect('courts')  # Redirect to courts list page

# User interface view
def user_interface(request):
    courts_data = Court.objects.all()
    
    # Update active status for each court
    for court in courts_data:
        court.update_active_status()

    context = {
        'courts': courts_data,
    }
    return render(request, 'app_home/user/user-interface.html', context)

# User registration view
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

        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Ensure groups 'Admin' and 'User' exist
        if role == 'Admin':
            group, created = Group.objects.get_or_create(name='Admin')
        else:
            group, created = Group.objects.get_or_create(name='User')
        
        user.groups.add(group)
        messages.success(request, "Registration successful! Please log in to continue.")

        return redirect('login')

    context = {
        'title': 'Đăng ký tài khoản',
        'message': 'Chào mừng bạn đến trang đăng ký!',
    }

    return render(request, 'app_home/user/register.html', context)

# User login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'app_home/user/login.html')

# Account view for logged-in user
@login_required
def account_view(request):
    user = request.user  # Get logged-in user

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        confirm_deletion = request.POST.get('confirm_deletion')  # Deletion confirmation

        # Ensure that first name and email are not empty
        if not first_name or not email:
            messages.error(request, "First Name và Email là bắt buộc!")
            return redirect('account')

        # Check if username is already taken
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại.")
            return redirect('account')

        # Handle account deletion
        if confirm_deletion:
            user.delete()  # Delete the user account
            messages.success(request, "Tài khoản của bạn đã được xóa.")
            return redirect('http://127.0.0.1:8000/')  # Redirect to home page after deletion

        # Update user information
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        messages.success(request, "Cập nhật thông tin thành công!")
        return redirect('home')  # Redirect to home page after successful update

    return render(request, 'app_home/user/account.html', {'user': user})
