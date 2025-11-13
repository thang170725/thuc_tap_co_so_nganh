from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myapp.models import Users, Courses, Classes, Schedules, Students_Classes, Students
from .forms import CourseForm, ClassForm

# Hàm tiện ích (lấy user_profile cho base.html)
def get_admin_profile(request):
    try:
        user_id = request.session.get('userId')
        if not user_id:
            return None
        return Users.objects.get(userId=user_id)
    except Users.DoesNotExist:
        return None

def course_list(request):
    """
    1. View (Read): Hiển thị danh sách Môn học
    """
    course_list = Courses.objects.all().order_by('courseId')

    context = {
        'course_list': course_list,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/course_list.html', context)

def course_create_edit(request, course_id=None):
    """
    2. View (Create/Update): Tạo/Sửa Môn học
    """
    if course_id:
        # Đây là Sửa (Update)
        course = get_object_or_404(Courses, courseId=course_id)
        form_title = f'Chỉnh sửa Môn học: {course.courseId}'
        is_editing = True
    else:
        # Đây là Tạo (Create)
        course = None
        form_title = 'Tạo Môn học mới'
        is_editing = False

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Lưu môn học '{form.cleaned_data['courseName']}' thành công!")
                return redirect('course_list')
            except Exception as e:
                # Bắt lỗi nếu Mã Môn học bị trùng (khi tạo mới)
                messages.error(request, f"Lỗi khi lưu: {e}")
    else:
        form = CourseForm(instance=course)
        
    # Khi Sửa, không cho sửa Mã Môn học (Khóa chính)
    if is_editing:
        form.fields['courseId'].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'form_title': form_title,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/course_form.html', context)


def course_delete(request, course_id):
    """
    3. View (Delete): Xóa Môn học
    """
    course = get_object_or_404(Courses, courseId=course_id)

    # (Kiểm tra an toàn)
    # Tìm xem có Lớp học (Classes) hoặc Lịch học (Schedules)
    # nào đang dùng Môn học này không
    
    # Do models.py của bạn không có related_name,
    # chúng ta dùng tên mặc định `tênmodel_set`
    # (Sửa lỗi: Phải dùng related_name hoặc tên _set)
    # Giả sử related_name trong models.py là:
    # Classes -> courseId = FK(Courses, related_name='classes')
    # Schedules -> courseId = FK(Courses, related_name='schedules')
    
    # CẬP NHẬT: Dùng tên _set mặc định của Django
    if course.classes_set.exists():
        messages.error(request, f"Lỗi: Không thể xóa môn '{course.courseName}'. Đã có Lớp học (Classes) đang sử dụng môn này.")
        return redirect('course_list')
        
    if course.schedules_set.exists():
        messages.error(request, f"Lỗi: Không thể xóa môn '{course.courseName}'. Đã có Lịch học (Schedules) đang sử dụng môn này.")
        return redirect('course_list')

    if request.method == 'POST':
        try:
            course_name = course.courseName
            course.delete()
            messages.success(request, f"Đã xóa môn học '{course_name}' thành công.")
            return redirect('course_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")

    context = {
        'course_to_delete': course,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/course_confirm_delete.html', context)
# ===============================================
# === PHẦN B: VIEWS QUẢN LÝ LỚP HỌC (CLASSES) ===
# ===============================================

def class_list(request):
    """
    1. View (Read): Hiển thị danh sách Lớp học
    """
    class_list = Classes.objects.all().select_related('courseId', 'teacher').order_by('classId')

    context = {
        'class_list': class_list,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/class_list.html', context)

def class_create_edit(request, class_id=None):
    """
    2. View (Create/Update): Tạo/Sửa Lớp học
    """
    if class_id:
        class_obj = get_object_or_404(Classes, classId=class_id)
        form_title = f'Chỉnh sửa Lớp học: {class_obj.classId}'
        is_editing = True
    else:
        class_obj = None
        form_title = 'Tạo Lớp học mới'
        is_editing = False

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Lưu lớp học '{form.cleaned_data['classId']}' thành công!")
                return redirect('class_list')
            except Exception as e:
                messages.error(request, f"Lỗi khi lưu: {e}. (Mã Lớp có thể đã bị trùng?)")
    else:
        form = ClassForm(instance=class_obj)
        
    if is_editing:
        form.fields['classId'].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'form_title': form_title,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/class_form.html', context)


# academic_manager/views.py

# ... (các import và view khác) ...

def class_delete(request, class_id):
    """
    3. View (Delete): Xóa Lớp học (Đã sửa lỗi)
    """
    class_obj = get_object_or_404(Classes, classId=class_id)

    # (Kiểm tra an toàn - ĐÃ SỬA LỖI)
    # Django tự động tạo ra 'students_classes_set' (hoặc 'studentsclasses_set')
    # trên model 'Classes' để trỏ ngược về Bảng Students_Classes
    
    # Kiểm tra xem 'classId' này có tồn tại trong
    # bảng Students_Classes không
    if class_obj.students_classes_set.exists(): 
        messages.error(request, f"Lỗi: Không thể xóa lớp '{class_obj.classId}'. Đã có Sinh viên được gán vào lớp này.")
        return redirect('class_list')

    if request.method == 'POST':
        try:
            class_name = class_obj.classId
            class_obj.delete()
            messages.success(request, f"Đã xóa lớp học '{class_name}' thành công.")
            return redirect('class_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")

    context = {
        'class_to_delete': class_obj,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/class_confirm_delete.html', context)
# === PHẦN C: VIEW GÁN SINH VIÊN VÀO LỚP ===
# ===============================================

def manage_class_students(request, class_id):
    """
    View (Create/Delete): Gán (Thêm) hoặc Hủy gán (Xóa) Sinh viên
    khỏi một Lớp học (Bảng Students_Classes)
    """
    class_obj = get_object_or_404(Classes, classId=class_id)
    
    # Xử lý POST (khi Admin bấm nút "Thêm" hoặc "Xóa")
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        
        try:
            student_obj = Students.objects.get(studentId=student_id)
            
            if action == 'add':
                # Dùng get_or_create để tránh lỗi nếu lỡ thêm 2 lần
                Students_Classes.objects.get_or_create(classId=class_obj, studentId=student_obj)
                messages.success(request, f"Đã thêm SV '{student_obj.fullName}' vào lớp.")
                
            elif action == 'remove':
                # Tìm và xóa bản ghi
                enrollment = Students_Classes.objects.filter(classId=class_obj, studentId=student_obj)
                if enrollment.exists():
                    enrollment.delete()
                    messages.success(request, f"Đã xóa SV '{student_obj.fullName}' khỏi lớp.")
                    
        except Students.DoesNotExist:
            messages.error(request, "Lỗi: Không tìm thấy sinh viên.")
        except Exception as e:
            messages.error(request, f"Lỗi: {e}")
        
        # Luôn tải lại trang sau khi POST
        return redirect('manage_class_students', class_id=class_id)
        

    # Xử lý GET (Hiển thị trang)
    
    # 1. Lấy danh sách ID các sinh viên ĐÃ CÓ trong lớp này
    enrolled_student_ids = Students_Classes.objects.filter(classId=class_obj).values_list('studentId', flat=True)
    
    # 2. Lấy thông tin các sinh viên ĐÃ CÓ trong lớp
    enrolled_students = Students.objects.filter(studentId__in=enrolled_student_ids).order_by('studentId')
    
    # 3. Lấy danh sách sinh viên CHƯA CÓ trong lớp (để Thêm)
    available_students = Students.objects.exclude(studentId__in=enrolled_student_ids).order_by('studentId')

    context = {
        'class_obj': class_obj,
        'enrolled_students': enrolled_students,
        'available_students': available_students,
        'user_profile': get_admin_profile(request) # Cho base.html
    }
    return render(request, 'academic_manager/manage_class_students.html', context)