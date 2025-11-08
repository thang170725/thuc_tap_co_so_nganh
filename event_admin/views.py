# event_admin/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Events
from .forms import EventForm
# (Giả sử bạn có decorator @admin_required để kiểm tra đăng nhập Admin)
# from django.contrib.auth.decorators import login_required

# @login_required
def event_management(request):
    """ 1. View: Hiển thị danh sách tất cả sự kiện """
    all_events = Events.objects.all() 
    context = {
        'events': all_events
    }
    return render(request, 'event_admin/event_list.html', context)

# @login_required
def event_create_update(request, event_id=None):
    """ 2. View: Dùng chung cho cả Tạo mới và Cập nhật """
    if event_id:
        event = get_object_or_404(Events, id=event_id)
        form_title = 'Cập nhật sự kiện'
    else:
        event = None
        form_title = 'Tạo sự kiện mới'

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã {form_title.lower()} thành công!')
            return redirect('event_management') # Về trang danh sách
        else:
            messages.error(request, 'Lỗi! Vui lòng kiểm tra lại thông tin.')
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'form_title': form_title
    }
    return render(request, 'event_admin/event_form.html', context)

# @login_required
def event_delete(request, event_id):
    """ 3. View: Xử lý xóa sự kiện (có xác nhận) """
    event = get_object_or_404(Events, id=event_id)
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Đã xóa sự kiện: {event_title}')
        return redirect('event_management')
    
    # Nếu là GET, chỉ hiển thị trang xác nhận
    context = {
        'event': event
    }
    return render(request, 'event_admin/event_confirm_delete.html', context)