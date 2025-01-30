from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Schedule, Court
from .forms import ScheduleForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import date, datetime, timedelta

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
def book_court(request, court_id):
    court = get_object_or_404(Court, id=court_id)
    today = date.today()  # Lấy ngày hiện tại dưới dạng datetime.date
    max_allowed_date = today + timedelta(days=9)  # Tính ngày xa nhất có thể đặt
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Xử lý AJAX (GET) để lấy giờ trống
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        selected_date_str = request.GET.get('date')  # Lấy ngày từ request

        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()  # Chuyển đổi sang datetime.date

                # Kiểm tra nếu ngày đã qua thì không cho phép
                if selected_date < today:
                    return JsonResponse({'error': 'Không thể chọn ngày trong quá khứ.'}, status=400)

                # Giới hạn lịch chỉ hiển thị đến max_allowed_date
                if selected_date > max_allowed_date:
                    return JsonResponse({'error': 'Nếu cần đặt ngày xa hơn, hãy gọi đến số hotline 9999 hoặc nhắn tin cho fanpage Nhom-2.'}, status=400)

                # Lấy danh sách giờ đã được đặt
                bookings = Schedule.objects.filter(court=court, date=selected_date).order_by('start_time')
                opening_time = court.OpeningHours
                closing_time = court.ClosingHours

                # Tính giờ trống
                available_slots = []
                current_time = opening_time

                for booking in bookings:
                    if current_time < booking.start_time:
                        available_slots.append(f"{current_time.strftime('%H:%M')} - {booking.start_time.strftime('%H:%M')}")
                    current_time = max(current_time, booking.end_time)

                if current_time < closing_time:
                    available_slots.append(f"{current_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}")

                return JsonResponse({'available_times': available_slots})

            except ValueError:
                return JsonResponse({'error': 'Ngày không hợp lệ.'}, status=400)

    # Xử lý POST để lưu lịch đặt
    elif request.method == 'POST':
        court = get_object_or_404(Court, id=court_id)  # Lấy court từ URL
        days = request.POST.getlist('days[]')  # Lấy danh sách ngày từ request
        form_data = request.POST.copy()
        form_data.setlist('days', days)
        print("Received days:", days)
        form = ScheduleForm(form_data)
        form.request = request  # Truyền request vào form để xử lý customer
        schedule_type = request.POST.get('schedule_type', '').strip()
        selected_date_str = request.POST.get('date', '').strip()
        print(f"Received date string: {selected_date_str}")
        print("Request POST data:", request.POST)
        print("Form data before sending to ScheduleForm:", form_data)

    # Chỉ kiểm tra date nếu loại lịch là Daily
        if schedule_type == "Daily":
            if not selected_date_str:
                form.add_error('date', "Vui lòng chọn ngày hợp lệ.")
            else:
                try:
                    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                    if selected_date < date.today():
                        form.add_error('date', "Không thể đặt lịch cho ngày đã qua.")
                except ValueError:
                    form.add_error('date', "Định dạng phải là YYYY-MM-DD.")
            
        else:
            selected_date = None  # Fixed và Flexible không cần ngày

        if form.is_valid():
            try:
                schedule = form.save(commit=False)
                schedule.clean()
                schedule.customer = request.user
                schedule.court = court  # Gán sân vào lịch
                schedule.days = days  # Gán giá trị từ checkbox

                if schedule_type == "Daily":
                    schedule.date = selected_date  # Chỉ cần cho Daily
                    date_str = request.POST.get("date", None)
                    if not date_str:
                        errors.append("Ngày không hợp lệ. Vui lòng chọn ngày.")
                else:
                    date_str = None  # Không kiểm tra ngày nếu không phải Daily
                    
                # Lưu lịch vào database
                schedule.save()
                messages.success(request, "Lịch đã được đặt thành công!")
                return redirect('schedule-list')

            except ValidationError as e:
                messages.error(request, f"Error: {e}")

        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
            return redirect('book-court', court_id=court_id)

    else:
        form = ScheduleForm()

    return render(request, 'app_home/schedule/book-court.html', {
        'form': form,
        'court': court,
        'days_of_week': days_of_week,
        'max_allowed_date': max_allowed_date.strftime('%Y-%m-%d'),  # Gửi biến này ra frontend
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

@login_required
@csrf_exempt
def check_schedule_conflict(request):
    print("Request GET data:", request.GET)

    court_id = request.GET.get('court_id')
    schedule_type = request.GET.get('schedule_type')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    total_hours = request.GET.get('total_hours')
    duration = request.GET.get('duration_fixed')

    # Kiểm tra tham số cơ bản
    if not court_id or not schedule_type:
        return JsonResponse({'error': 'Missing required parameters.'}, status=400)

    if schedule_type != "Fixed":
        duration = None  # Loại bỏ giá trị duration nếu không phải lịch cố định

    try:
        # Chuyển đổi dữ liệu
        date = datetime.strptime(date, "%Y-%m-%d").date() if date else None
        start_time = datetime.strptime(start_time, "%H:%M").time() if start_time else None
        end_time = datetime.strptime(end_time, "%H:%M").time() if end_time else None

        # Lấy danh sách lịch liên quan
        conflicts = Schedule.objects.filter(court_id=court_id)

        if schedule_type == 'Daily':
            if not date or not start_time or not end_time:
                return JsonResponse({'error': 'Daily schedule requires date, start time, and end time.'}, status=400)

            conflicts = conflicts.filter(
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

        elif schedule_type == 'Fixed':
            if not days or not start_time or not end_time or not duration:
                return JsonResponse({'error': 'Fixed schedule requires days, duration, start time, and end time.'}, status=400)

            if days:
                day_of_week = date.strftime('%A')
                conflicts = conflicts.filter(
                    days__overlap=days,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )

        elif schedule_type == 'Flexible':
            total_hours = request.GET.get('total_hours')
            if not total_hours:
                return JsonResponse({'error': 'Total hours are required for Flexible schedule.'}, status=400)

        # Kiểm tra và phản hồi
        if conflicts.exists():
            return JsonResponse({
                'conflict': True,
                'message': "Schedule conflicts with another booking."
            })
        else:
            return JsonResponse({'conflict': False})

    except Exception as e:
        print(f"Error in check_schedule_conflict: {e}")
        return JsonResponse({'error': str(e)}, status=400)
