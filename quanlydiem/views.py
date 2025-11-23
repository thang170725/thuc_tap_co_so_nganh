from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
# Import đúng tên Model số nhiều như trong myapp/models.py
from myapp.models import Classes, Grades, Students_Classes, Students, Teachers
from myapp.views import fetch_username

# 1. View Giảng viên nhập điểm
def teacher_input_grades(request, class_id):
    # SỬA: Class -> Classes
    lop_hoc = get_object_or_404(Classes, classId=class_id)
    
    # SỬA: 
    # 1. filter(class_obj=...) -> filter(classId=...) (vì trong Students_Classes tên cột là classId)
    # 2. select_related('student') -> select_related('studentId') (vì tên cột là studentId)
    danh_sach_sv = Students_Classes.objects.filter(classId=lop_hoc).select_related('studentId')
    
    # SỬA: Grade -> Grades
    diem_hien_co = Grades.objects.filter(class_obj=lop_hoc)
    
    # Tạo dictionary để tra cứu điểm nhanh
    # Lưu ý: g.student trả về object Students, g.student.pk trả về mã SV (string)
    dict_diem = {g.student.pk: g for g in diem_hien_co}

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for item in danh_sach_sv:
                    # SỬA: item.student -> item.studentId (vì ForeignKey tên là studentId)
                    sv = item.studentId 
                    ma_sv = sv.pk # Lấy khóa chính (studentId string)
                    
                    # Lấy dữ liệu từ form
                    cc = request.POST.get(f'cc_{ma_sv}')
                    gk = request.POST.get(f'gk_{ma_sv}')
                    ck = request.POST.get(f'ck_{ma_sv}')
                    
                    # Xử lý input rỗng
                    cc = float(cc) if cc else 0
                    gk = float(gk) if gk else 0
                    ck = float(ck) if ck else 0

                    # SỬA: Grade -> Grades
                    Grades.objects.update_or_create(
                        student=sv,
                        class_obj=lop_hoc,
                        defaults={
                            'attendanceScore': cc,
                            'midtermScore': gk,
                            'finalScore': ck
                        }
                    )
            return redirect('teacher_input_grades', class_id=class_id)
        except Exception as e:
            print(f"Lỗi: {e}")

    # Chuẩn bị dữ liệu ra template
    data_hien_thi = []
    for item in danh_sach_sv:
        # SỬA: item.student -> item.studentId
        sv = item.studentId
        diem = dict_diem.get(sv.pk)
        data_hien_thi.append({'sv': sv, 'diem': diem})

    return render(request, 'quanlydiem/teacher_input.html', {
        'lop': lop_hoc,
        'data': data_hien_thi
    })

'''
=========================================
======== VIEW SINH VIÊN XEM ĐIỂM ========
=========================================
'''
def student_my_grades(request):
    user_id = request.session.get('userId')
    # TODO: Sau này thay bằng request.user.username hoặc logic lấy sinh viên từ session
    ma_sv_hien_tai = 'S001' 
    
    # SỬA: Student -> Students
    student = get_object_or_404(Students, studentId=ma_sv_hien_tai)
    username = fetch_username(user_id)
    bang_diem = Grades.objects.filter(student=student).select_related('class_obj', 'class_obj__courseId')
    context = {
        'studentId': user_id,
        'username': username,
        'user_role': 'STUDENT',
        'bang_diem': bang_diem
    }
    return render(request, 'quanlydiem/grades.html', context)

# 3. View Dashboard (Thêm cái này để nút Sidebar hoạt động)
def teacher_grade_dashboard(request):
    # Tạm thời hardcode giáo viên T001
    current_teacher_id = 'T001' 
    
    # SỬA: Lấy danh sách lớp theo teacherId, select_related courseId
    classes = Classes.objects.filter(teacher__teacherId=current_teacher_id).select_related('courseId')
    
    return render(request, 'quanlydiem/teacher_dashboard.html', {'classes': classes})