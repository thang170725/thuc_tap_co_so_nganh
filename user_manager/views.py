# user_manager/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, connection
# (Xóa import DjangoUser)
from myapp.models import Users, Students, Teachers, Admins
from .forms import UserCreateForm, UserEditForm

# Hàm tiện ích (lấy user_profile cho base.html)
def get_admin_profile(request):
    try:
        user_id = request.session.get('userId')
        if not user_id:
            return None
        return Users.objects.get(userId=user_id)
    except Users.DoesNotExist:
        return None

def user_list(request):
    """
    1. View (Read): Hiển thị danh sách (Code này đã đúng)
    """
    role_filter = request.GET.get('role')
    
    if role_filter in ['student', 'teacher', 'admin']:
        user_list = Users.objects.filter(role=role_filter).order_by('userId')
    else:
        user_list = Users.objects.all().order_by('role', 'userId')

    context = {
        'user_list': user_list,
        'user_profile': get_admin_profile(request)
    }
    return render(request, 'user_manager/user_list.html', context)

def user_create(request):
    """
    2. View (Create): Tạo người dùng mới (Đã sửa)
    """
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            userId = form.cleaned_data['userId']
            password = form.cleaned_data['password'] # Mật khẩu plain text
            email = form.cleaned_data['email']
            fullName = form.cleaned_data['fullName']
            role = form.cleaned_data['role']

            # Kiểm tra xem UserID đã tồn tại chưa (Chỉ trong bảng Users)
            if Users.objects.filter(userId=userId).exists():
                messages.error(request, f"Lỗi: Tên đăng nhập '{userId}' đã tồn tại.")
                form = UserCreateForm(request.POST)
            else:
                try:
                    # Dùng transaction để đảm bảo tất cả cùng thành công
                    with transaction.atomic():
                        
                        # 1. Tạo user trong bảng Users của bạn
                        custom_user = Users.objects.create(
                            userId=userId,
                            passwordHash=password, # Lưu mật khẩu plain text (theo logic login_view của bạn)
                            email=email,
                            role=role
                        )
                        
                        # 2. Tạo profile chi tiết
                        if role == 'student':
                            Students.objects.create(studentId=custom_user, fullName=fullName)
                        elif role == 'teacher':
                            Teachers.objects.create(teacherId=custom_user, fullName=fullName)
                        elif role == 'admin':
                            Admins.objects.create(adminId=custom_user, fullName=fullName)

                    messages.success(request, f"Tạo người dùng '{userId}' thành công!")
                    return redirect('user_list')
                
                except Exception as e:
                    messages.error(request, f"Lỗi nghiêm trọng khi tạo user: {e}")
    
    else:
        form = UserCreateForm()

    context = {
        'form': form,
        'form_title': 'Tạo Người dùng mới',
        'user_profile': get_admin_profile(request)
    }
    return render(request, 'user_manager/user_form.html', context)


def user_edit(request, user_id):
    """
    3. View (Update): Chỉnh sửa thông tin (Đã sửa)
    """
    try:
        # CHỈ LẤY user từ bảng 'Users' của bạn
        custom_user = Users.objects.get(userId=user_id)
        
        profile_obj = None
        if custom_user.role == 'student':
            profile_obj = Students.objects.get(studentId=custom_user)
        elif custom_user.role == 'teacher':
            profile_obj = Teachers.objects.get(teacherId=custom_user)
        elif custom_user.role == 'admin':
            profile_obj = Admins.objects.get(adminId=custom_user)
            
    except Users.DoesNotExist:
        messages.error(request, "Không tìm thấy người dùng này.")
        return redirect('user_list')
    except (Students.DoesNotExist, Teachers.DoesNotExist, Admins.DoesNotExist):
        profile_obj = None # Vẫn cho sửa email/role

    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            new_fullName = form.cleaned_data['fullName']
            new_email = form.cleaned_data['email']
            new_role = form.cleaned_data['role'] 
            
            try:
                with transaction.atomic():
                    # Cập nhật Bảng Users
                    custom_user.email = new_email
                    custom_user.role = new_role 
                    custom_user.save()
                    
                    # Cập nhật Bảng profile
                    if profile_obj:
                        profile_obj.fullName = new_fullName
                        profile_obj.save()
                        
                messages.success(request, f"Cập nhật '{user_id}' thành công.")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Lỗi khi cập nhật: {e}")
            
    else:
        # GET: Hiển thị thông tin hiện tại
        form = UserEditForm(initial={
            'email': custom_user.email,
            'fullName': profile_obj.fullName if profile_obj else '',
            'role': custom_user.role
        })

    context = {
        'form': form,
        'form_title': f'Chỉnh sửa: {user_id}',
        'user_profile': get_admin_profile(request)
    }
    return render(request, 'user_manager/user_form.html', context)


def user_delete(request, user_id):
    """
    4. View (Delete): Xóa người dùng (Đã sửa)
    """
    try:
        # CHỈ LẤY user từ bảng 'Users' của bạn
        custom_user = Users.objects.get(userId=user_id)
        
    except Users.DoesNotExist:
        messages.error(request, "Không tìm thấy người dùng này.")
        return redirect('user_list')

    if request.method == 'POST':
        try:
            user_name = custom_user.userId
            
            # Xóa user khỏi Bảng Users.
            # Do 'on_delete=CASCADE' trong models.py,
            # user trong 'Students'/'Teachers'/'Admins' sẽ tự động bị xóa theo.
            custom_user.delete()
            
            messages.success(request, f"Đã xóa người dùng '{user_name}' thành công.")
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")

    context = {
        'user_to_delete': custom_user,
        'user_profile': get_admin_profile(request)
    }
    return render(request, 'user_manager/user_confirm_delete.html', context)