from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
# --- THÊM IMPORT NÀY ĐỂ TÍNH TOÁN THỐNG KÊ ---
from django.db.models import Count, Q 
from datetime import date
from .forms import AttendanceFormSet
from myapp.models import Classes, Teachers, Courses, Students_Classes, Students, Attendances
from django.shortcuts import render, redirect
from django.db import connection
from django.utils import timezone

# ======================== HÀM PHỤ TRANG GIẢNG VIÊN ========================
def fetch_teachername(user_id):
  with connection.cursor() as cursor:
    cursor.execute('''
      select fullName
      from Teachers
      where teacherId = %s 
    ''', [user_id])
    row = cursor.fetchone()
  return row[0] if row else None

def teacher_attendance(request, class_id):
    # Lấy danh sách sinh viên trong lớp
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.studentId, s.fullName
            FROM Students s
            join Students_Classes sl on s.studentId = sl.studentId
            JOIN Classes cl ON sl.classId = cl.classId 
            WHERE sl.classId = %s
        """, [class_id])
        students_result = cursor.fetchall()

    students = [{'studentId': s[0], 'fullName': s[1]} for s in students_result]

    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        if not attendance_date:
            attendance_date = timezone.now().date()  # mặc định ngày hôm nay

        with connection.cursor() as cursor:
            for student in students:
                student_id = student['studentId']
                status = request.POST.get(f'status_{student_id}', 'PRESENT')
                note = request.POST.get(f'note_{student_id}', '')

                # Kiểm tra nếu bản ghi đã tồn tại cho ngày đó
                cursor.execute("""
                    SELECT attendanceId FROM Attendances
                    WHERE classId=%s AND studentId=%s AND date=%s
                """, [class_id, student_id, attendance_date])
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE Attendances
                        SET status=%s, note=%s, created_at=CURRENT_TIMESTAMP
                        WHERE attendanceId=%s
                    """, [status, note, existing[0]])
                else:
                    cursor.execute("""
                        INSERT INTO Attendances(classId, studentId, date, status, note)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [class_id, student_id, attendance_date, status, note])

        return redirect('teacher_attendance', class_id=class_id)

    # lấy tên giảng viên
    user_id = request.session.get('userId')
    print("DEBUG userId =", request.session.get('userId'))
    if not user_id:
        return redirect('login')
    username = fetch_teachername(user_id)
    context = {
        'username': username,
        'user_role': 'TEACHER',
        'class_id': class_id,
        'students': students,
        'today': timezone.now().date()
    }
    return render(request, 'attendance_module/teacher_attendance.html', context)

def teacher_class_list(request):
    # GIẢ ĐỊNH: Giảng viên hiện tại là 'T001'
    current_teacher_id = 'T001' 
    
    # Lấy thông tin giảng viên
    teacher = Teachers.objects.filter(teacherId=current_teacher_id).first()
    
    # Lấy tất cả các lớp học do giảng viên này phụ trách
    classes_taught = Classes.objects.filter(teacher_id=current_teacher_id)
    
    # Lấy tên môn học tương ứng
    course_ids = [c.courseId_id for c in classes_taught]
    
    courses_query = Courses.objects.filter(courseId__in=course_ids)
    courses_dict = {
        c.courseId: c.courseName 
        for c in courses_query
    }
    
    class_list = []
    for cls in classes_taught:
        class_list.append({
            'classId': cls.classId,
            'courseName': courses_dict.get(cls.courseId_id, 'Không tìm thấy'), 
            'semester': cls.semester
        })
    
    context = {
        'teacher_name': teacher.fullName if teacher else 'Giảng viên',
        'class_list': class_list
    }
    return render(request, 'attendance_module/class_list.html', context)


def teacher_attendance_view(request, class_id):
    current_class = get_object_or_404(Classes, classId=class_id)
    attendance_date = date.today() 

    # 1. Lấy danh sách studentId trong lớp
    student_ids_in_class = list(
        Students_Classes.objects.filter(classId=class_id).values_list('studentId', flat=True)
    )
    
    student_details = Students.objects.filter(studentId__in=student_ids_in_class).order_by('studentId')
    student_dict = {s.studentId: s.fullName for s in student_details}

    # --- [MỚI] TÍNH TOÁN THỐNG KÊ (Tổng Nghỉ/Muộn) ---
    # Logic: Nhóm theo studentId, đếm số dòng có status là ABSENT hoặc LATE
    stats_query = Attendances.objects.filter(classId=class_id).values('studentId').annotate(
        total_absent=Count('pk', filter=Q(status='ABSENT')),
        total_late=Count('pk', filter=Q(status='LATE'))
    )
    # Chuyển QuerySet thành Dictionary để tra cứu nhanh: {'SV001': {'a': 2, 'l': 1}, ...}
    stats_map = {
        item['studentId']: {'absent': item['total_absent'], 'late': item['total_late']} 
        for item in stats_query
    }
    # -------------------------------------------------

    # 2. Kiểm tra các bản ghi điểm danh ĐÃ TỒN TẠI
    existing_attendances = Attendances.objects.filter(
        classId=class_id, 
        date=attendance_date
    ).filter(studentId__in=student_ids_in_class).order_by('studentId')

    initial_data = []

    if existing_attendances.exists():
        queryset = existing_attendances
    else:
        queryset = Attendances.objects.none()
        for s_id in student_ids_in_class:
            initial_data.append({
                'studentId': s_id,
                'classId': class_id,
                'date': attendance_date,
                'status': 'PRESENT', 
            })

    # Khởi tạo Formset
    formset = AttendanceFormSet(
        request.POST or None, 
        queryset=queryset,
        initial=initial_data if not existing_attendances.exists() else None
    )

    # Xử lý khi Submit
    if request.method == 'POST' and formset.is_valid():
        instances = formset.save(commit=False)
        
        for instance in instances:
            instance.classId = class_id
            instance.date = attendance_date
            try:
                instance.save()
            except IntegrityError:
                pass 
                
        if existing_attendances.exists():
            formset.save_m2m() 
        
        return redirect('attendance_success') 

    # Thêm dữ liệu vào từng form để hiển thị Template
    for form in formset:
        # Lấy studentId (dù là form edit hay form new)
        s_id = form.initial.get('studentId') or form.instance.studentId
        
        if s_id:
            # 1. Gán tên sinh viên
            form.full_name = student_dict.get(s_id, 'Không rõ tên')
            
            # 2. [MỚI] Gán thống kê (Lấy từ map, nếu không có thì bằng 0)
            stat = stats_map.get(s_id, {'absent': 0, 'late': 0})
            form.stats_absent = stat['absent']
            form.stats_late = stat['late']

    context = {
        'current_class': current_class,
        'attendance_date': attendance_date,
        'formset': formset,
    }
    return render(request, 'attendance_module/attendance_form.html', context)


def attendance_success(request):
    return render(request, 'attendance_module/attendance_success.html')