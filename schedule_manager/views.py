from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myapp.models import Users, Rooms, Schedules # <-- Import Rooms, Schedules
from .forms import RoomForm, ScheduleForm

# Hàm tiện ích (lấy user_profile cho base.html)
def get_admin_profile(request):
    try:
        user_id = request.session.get('userId')
        if not user_id:
            return None
        return Users.objects.get(userId=user_id)
    except Users.DoesNotExist:
        return None

# ===============================================
# === PHẦN A: VIEWS QUẢN LÝ PHÒNG HỌC (ROOMS) ===
# ===============================================

def room_list(request):
    """
    1. View (Read): Hiển thị danh sách Phòng học
    """
    room_list = Rooms.objects.all().order_by('building', 'roomNumber')

    context = {
        'room_list': room_list,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/room_list.html', context)

def room_create_edit(request, room_id=None):
    """
    2. View (Create/Update): Tạo/Sửa Phòng học
    """
    if room_id:
        # Đây là Sửa (Update)
        room = get_object_or_404(Rooms, roomId=room_id)
        form_title = f'Chỉnh sửa Phòng học: {room.roomId}'
        is_editing = True
    else:
        # Đây là Tạo (Create)
        room = None
        form_title = 'Tạo Phòng học mới'
        is_editing = False

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Lưu phòng '{form.cleaned_data['roomNumber']}' thành công!")
                return redirect('room_list')
            except Exception as e:
                messages.error(request, f"Lỗi khi lưu: {e}. (Mã Phòng có thể đã bị trùng?)")
    else:
        form = RoomForm(instance=room)
        
    # Khi Sửa, không cho sửa Mã Phòng (Khóa chính)
    if is_editing:
        form.fields['roomId'].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'form_title': form_title,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/room_form.html', context)


def room_delete(request, room_id):
    """
    3. View (Delete): Xóa Phòng học
    """
    room = get_object_or_404(Rooms, roomId=room_id)

    # (Kiểm tra an toàn)
    # Model Schedules của bạn có FK 'roomId' trỏ đến Rooms
    # Tên trỏ ngược (related_name) mặc định là 'schedules_set'
    if room.schedules_set.exists():
        messages.error(request, f"Lỗi: Không thể xóa phòng '{room.roomNumber}'. Phòng này đang được sử dụng trong Thời khóa biểu (Schedules).")
        return redirect('room_list')

    if request.method == 'POST':
        try:
            room_name = room.roomNumber
            room.delete()
            messages.success(request, f"Đã xóa phòng học '{room_name}' thành công.")
            return redirect('room_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")

    context = {
        'room_to_delete': room,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/room_confirm_delete.html', context)
# === PHẦN B: VIEWS QUẢN LÝ TKB (SCHEDULES) ===
# ===============================================

def schedule_list(request):
    """
    1. View (Read): Hiển thị danh sách TKB (toàn trường)
    """
    schedule_list = Schedules.objects.all().select_related(
        'classId', 
        'roomId', 
        'classId__courseId', # Lấy luôn Môn học
        'classId__teacher'   # Lấy luôn Giảng viên
    ).order_by('dayOfWeek', 'startTime')

    context = {
        'schedule_list': schedule_list,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/schedule_list.html', context)


def schedule_create_edit(request, schedule_id=None):
    """
    2. View (Create/Update): Tạo/Sửa Lịch học
    """
    if schedule_id:
        # Đây là Sửa (Update)
        schedule = get_object_or_404(Schedules, scheduleId=schedule_id)
        form_title = f'Chỉnh sửa Lịch học: {schedule.scheduleId}'
        is_editing = True
    else:
        # Đây là Tạo (Create)
        schedule = None
        form_title = 'Tạo Lịch học mới'
        is_editing = False

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Lưu lịch học thành công!")
                return redirect('schedule_list')
            except Exception as e:
                messages.error(request, f"Lỗi khi lưu: {e}. (Mã Lịch học có thể đã bị trùng?)")
        else:
            messages.error(request, "Lỗi: Dữ liệu không hợp lệ. Vui lòng kiểm tra các lỗi bên dưới.")
            # Form (với các lỗi trùng lặp) sẽ được render lại
            
    else:
        form = ScheduleForm(instance=schedule)
        
    # Khi Sửa, không cho sửa Mã Lịch (Khóa chính)
    if is_editing:
        form.fields['scheduleId'].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'form_title': form_title,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/schedule_form.html', context)


def schedule_delete(request, schedule_id):
    """
    3. View (Delete): Xóa Lịch học
    """
    schedule = get_object_or_404(Schedules, scheduleId=schedule_id)

    if request.method == 'POST':
        try:
            schedule_name = schedule.scheduleId
            schedule.delete()
            messages.success(request, f"Đã xóa lịch học '{schedule_name}' thành công.")
            return redirect('schedule_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")

    context = {
        'schedule_to_delete': schedule,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'schedule_manager/schedule_confirm_delete.html', context)