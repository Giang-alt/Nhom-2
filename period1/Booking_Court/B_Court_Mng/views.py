from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Schedule, Court
from .forms import ScheduleForm

def Courts(request):
    return HttpResponse("Hello world!")

@login_required
def schedule_list(request):
    if request.user.is_staff:  # Nhân viên hoặc admin sẽ thấy toàn bộ lịch
        schedules = Schedule.objects.all()
    else:  # Người dùng thường chỉ thấy lịch của họ
        schedules = Schedule.objects.filter(customer=request.user)
    return render(request, 'app_home/schedule/schedule-list.html', {'schedules': schedules})

@login_required
def book_court(request):
    courts = Court.objects.all()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'POST':
        print("POST data:", request.POST)
        form = ScheduleForm(request.POST)
        form.request = request  # Truyền request vào form để xử lý customer

        if form.is_valid():
            try:
                # Tạo đối tượng Schedule nhưng chưa lưu vào database
                schedule = form.save(commit=False)
                if not schedule.customer:
                    schedule.customer = request.user
                
                # Kiểm tra xung đột lịch
                schedule.save()  # Lưu lịch vào database
                messages.success(request, "Schedule booked successfully!")
                return redirect('schedule-list')
            except ValidationError as e:
                messages.error(request, f"Error: {e}")
        else:
            # Hiển thị lỗi dễ đọc
            errors = form.errors.as_data()
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error.message}")

    else:
        form = ScheduleForm()

    return render(request, 'app_home/schedule/book-court.html', {
        'form': form,
        'courts': courts,
        'days_of_week': days_of_week,
    })

@login_required
def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        form.request = request  # Truyền request vào form để xử lý customer

        if form.is_valid():
            try:
                # Kiểm tra và lưu lại lịch
                schedule = form.save(commit=False)
                if not schedule.customer:  # Đảm bảo customer được gán
                    schedule.customer = request.user
                schedule.clean()
                schedule.save()
                messages.success(request, "Schedule updated successfully!")
                return redirect('schedule-list')
            except ValidationError as e:
                # Hiển thị thông báo lỗi từ ValidationError
                messages.error(request, f"Error: {e}")
        else:
            # Hiển thị lỗi từ form
            messages.error(request, f"There was an error with your update: {form.errors.as_json()}")
    else:
        form = ScheduleForm(instance=schedule)

    return render(request, 'app_home/schedule/edit-schedule.html', {'form': form})

@login_required
def delete_schedule(request, id):
    schedule = get_object_or_404(Schedule, id=id)
    schedule.delete()
    messages.success(request, "Schedule deleted successfully!")
    return redirect('schedule-list')
