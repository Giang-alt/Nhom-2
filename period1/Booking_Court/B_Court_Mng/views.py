from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Schedule, Court
from .forms import ScheduleForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import date, datetime, timedelta
from decimal import Decimal

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
                now = datetime.now()

                if selected_date == today:
                    current_time = now.time()
                else:
                    current_time = opening_time

                # Tính giờ trống
                available_slots = []
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
        
        # Kiểm tra lịch Flexible
        if schedule_type == "Flexible":
            existing_flexible_schedule = Schedule.objects.filter(
                customer=request.user,
                schedule_type='Flexible',
                created_at__year=datetime.today().year,
                created_at__month=datetime.today().month,
            )
            if existing_flexible_schedule.exists():
                messages.error(request, "Bạn đã có lịch linh hoạt trong tháng này. Không thể đặt thêm lịch mới.")
                return redirect('book-court', court_id=court_id)

        # Kiểm tra form hợp lệ và xử lý
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
                return redirect('payment', id=schedule.id)

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

# @login_required
# def edit_schedule(request, schedule_id):
#     schedule = get_object_or_404(Schedule, id=schedule_id)

#     if request.method == 'POST':
#         form = ScheduleForm(request.POST, instance=schedule)
#         form.request = request  # Truyền request vào form để xử lý customer

#         if form.is_valid():
#             try:
#                 # Kiểm tra và lưu lại lịch
#                 schedule = form.save(commit=False)
#                 if not schedule.customer:  # Đảm bảo customer được gán
#                     schedule.customer = request.user
#                 schedule.clean()
#                 schedule.save()
#                 messages.success(request, "Schedule updated successfully!")
#                 return redirect('schedule-list')
#             except ValidationError as e:
#                 # Hiển thị thông báo lỗi từ ValidationError
#                 messages.error(request, f"Error: {e}")
#         else:
#             # Hiển thị lỗi từ form
#             messages.error(request, f"There was an error with your update: {form.errors.as_json()}")
#     else:
#         form = ScheduleForm(instance=schedule)

#     return render(request, 'app_home/schedule/edit-schedule.html', {'form': form})

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
    days = request.GET.getlist('days[]', [])

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

@login_required
def get_available_fixed_time_slots(request, court_id):
    """API lấy danh sách giờ trống cho lịch Fixed"""
    court = get_object_or_404(Court, id=court_id)
    selected_day = request.GET.get('day')

    if not selected_day:
        return JsonResponse({'error': 'Vui lòng chọn một ngày trong tuần.'}, status=400)

    opening_time = court.OpeningHours
    closing_time = court.ClosingHours

    # Lấy tất cả lịch Fixed xung đột trong sân và ngày được chọn
    conflicting_schedules = Schedule.objects.filter(
        court=court,
        schedule_type='Fixed',
        days__contains=[selected_day]
    ).order_by('start_time')

    available_slots = []
    current_time = opening_time

    for booking in conflicting_schedules:
        if current_time < booking.start_time:
            available_slots.append(f"{current_time.strftime('%H:%M')} - {booking.start_time.strftime('%H:%M')}")
        current_time = max(current_time, booking.end_time)

    # Thêm khung giờ cuối nếu còn giờ trống
    if current_time < closing_time:
        available_slots.append(f"{current_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}")

    return JsonResponse({'available_slots': available_slots})

@login_required
def payment(request, id):
    # Lấy đối tượng Schedule từ cơ sở dữ liệu hoặc trả về lỗi 404 nếu không tìm thấy
    schedule = get_object_or_404(Schedule, id=id)
    today = datetime.today().date()

    # Tính tổng tiền thanh toán
    total_price = Decimal(0)
    total_hours_text = "N/A"
    schedule_date = "Unknown Date"

    if schedule.schedule_type == 'Daily':
        # Kiểm tra nếu lịch đặt là quá khứ
        if schedule.date and schedule.date < today:
            messages.error(request, "Cannot process payment for past bookings.")
            return redirect('schedule-list')
        schedule_date = schedule.date.strftime('%d/%m/%Y') if schedule.date else "Unknown Date"
        start_time = datetime.combine(today, schedule.start_time)
        end_time = datetime.combine(today, schedule.end_time)
        duration = Decimal((end_time - start_time).total_seconds() / 3600)
        is_weekend = today.weekday() >= 5
        price_per_hour = schedule.court.WeekendPrice if is_weekend else schedule.court.WeekdayPrice
        total_price = price_per_hour * duration
        total_hours_text = f"{duration:.1f}h"

    elif schedule.schedule_type == 'Flexible' and schedule.total_hours:
        # Tính tổng giá cho lịch linh hoạt
        duration = Decimal(schedule.total_hours)
        is_weekend = today.weekday() >= 5
        price_per_hour = schedule.court.WeekendPrice if is_weekend else schedule.court.WeekdayPrice
        total_price = price_per_hour * duration
        total_hours_text = f"{duration}h (Monthly)"

    elif schedule.schedule_type == 'Fixed':
        # Tính tổng giá cho lịch cố định
        selected_days = schedule.days if schedule.days else []
        duration_months = schedule.duration
        start_time = schedule.start_time
        end_time = schedule.end_time
        duration = Decimal((datetime.combine(today, end_time) - datetime.combine(today, start_time)).total_seconds() / 3600)
        total_weeks = Decimal(duration_months * 4.33)
        total_sessions = len(selected_days) * total_weeks
        total_price = Decimal(0)
        for day in selected_days:
            is_weekend = day in ["Saturday", "Sunday"]
            price_per_hour = schedule.court.WeekendPrice if is_weekend else schedule.court.WeekdayPrice
            price_per_session = price_per_hour * duration
            total_price += price_per_session
        total_price *= total_weeks
        total_hours_text = f"{duration}h per session × {len(selected_days)} days/week × {duration_months} months"

    if total_price < 100000:
        total_price *= 1000

    formatted_total_price = str(int(total_price))

    # Xử lý khi nhấn "Confirm Payment"
    if request.method == 'POST':
        try:
            schedule.status = 'paid'  # Cập nhật trạng thái
            schedule.save()
            return redirect('/schedules/')  # Chuyển hướng về trang danh sách lịch
        except Exception as e:
            messages.error(request, f"Error processing payment: {e}")
            return redirect('/schedules/')

    return render(request, 'app_home/payment/payment.html', {
        'schedule': schedule,
        'schedule_date': schedule_date,
        'total_price': formatted_total_price,
        'today': today,
        'total_hours_text': total_hours_text,
    })

@login_required
def cancel_payment(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        schedule.delete()  # Xóa lịch đặt
    except Schedule.DoesNotExist:
        pass  # Nếu không tìm thấy lịch, tiếp tục mà không báo lỗi
    
    # Xóa toàn bộ messages cũ để tránh hiển thị thông báo đặt lịch thành công
    storage = get_messages(request)
    for _ in storage:
        pass  # Lặp qua để xóa tất cả messages trước đó

    # Thêm thông báo mới
    messages.error(request, "Payment failed! Please book again and complete the payment.")

    return redirect('schedule-list')
