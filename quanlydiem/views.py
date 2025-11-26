from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
# Import đúng tên Model số nhiều như trong myapp/models.py
from myapp.models import Classes, Grades, Students_Classes, Students, Teachers
from myapp.views import fetch_username
from django.db import connection

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from myapp.views import fetch_teachername

'''
=========================================
======== VIEW GIÁO VIÊN NHẬP ĐIỂM =======
=========================================
'''
def teacher_input_grades(request, class_id):
    # Lấy danh sách học sinh trong lớp
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.studentId, s.fullName, g.tx1, g.tx2, g.giua_ky, g.cuoi_ky, g.diem_trung_binh
            FROM Students s
            LEFT JOIN Grades g
            ON s.studentId = g.studentId AND g.classId = %s
            WHERE s.studentId IN (
                SELECT studentId FROM Students WHERE classId=%s
            )
        """, [class_id, class_id])
        result = cursor.fetchall()

    students = []
    for s in result:
        students.append({
            'studentId': s[0],
            'fullName': s[1],
            'tx1': s[2],
            'tx2': s[3],
            'giua_ky': s[4],
            'cuoi_ky': s[5],
            'diem_trung_binh': s[6],
        })

    if request.method == 'POST':
        with connection.cursor() as cursor:
            for student in students:
                student_id = student['studentId']

                tx1 = request.POST.get(f"tx1_{student_id}")
                tx2 = request.POST.get(f"tx2_{student_id}")
                giua_ky = request.POST.get(f"giua_ky_{student_id}")
                cuoi_ky = request.POST.get(f"cuoi_ky_{student_id}")

                try:
                    tx1 = float(tx1) if tx1 else None
                    tx2 = float(tx2) if tx2 else None
                    giua_ky = float(giua_ky) if giua_ky else None
                    cuoi_ky = float(cuoi_ky) if cuoi_ky else None
                except ValueError:
                    tx1 = tx2 = giua_ky = cuoi_ky = None

                # Kiểm tra xem bản ghi đã tồn tại
                cursor.execute("""
                    SELECT gradeId FROM Grades
                    WHERE studentId = %s AND classId = %s
                """, [student_id, class_id])
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE Grades
                        SET tx1=%s, tx2=%s, giua_ky=%s, cuoi_ky=%s, created_at=CURRENT_TIMESTAMP
                        WHERE gradeId=%s
                    """, [tx1, tx2, giua_ky, cuoi_ky, existing[0]])
                else:
                    cursor.execute("""
                        INSERT INTO Grades(studentId, classId, tx1, tx2, giua_ky, cuoi_ky)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [student_id, class_id, tx1, tx2, giua_ky, cuoi_ky])

        return redirect('teacher_input_grades', class_id=class_id)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.courseName FROM Courses c
                join Classes cl on c.courseId = cl.courseId
                join Grades g on cl.classId = g.classId
                WHERE cl.classId = %s
            """, [class_id])
        row = cursor.fetchone()
        courseName = row[0] if row else None
    
    # lấy tên giảng viên
    user_id = request.session.get('userId')
    print("DEBUG userId =", request.session.get('userId'))
    if not user_id:
        return redirect('login')
    username = fetch_teachername(user_id)

    context = {
        'lop': {'classId': class_id, 'courseName': courseName},  # update tên môn nếu cần
        'students': students,
        'username': username
    }
    return render(request, 'quanlydiem/teacher_input.html', context)

'''
=========================================
======== VIEW SINH VIÊN XEM ĐIỂM ========
=========================================
'''
def student_my_grades(request):
    user_id = request.session.get('userId')
    username = fetch_username(user_id)
    with connection.cursor() as cursor:
        cursor.execute('''
            select c.courseName, cl.classId, c.credits, g.tx1, g.tx2, g.giua_ky, g.cuoi_ky,  
                g.diem_trung_binh, g.created_at
            from Courses c
            join Classes cl on c.courseId = cl.courseId
            join Grades g on cl.classId = g.classId
            join Students s on g.studentId = s.StudentId
            where s.studentId = %s
            ORDER BY g.created_at DESC;
        ''', [user_id])
        rows = cursor.fetchall()

    grades_list = []
    for row in rows:
        grades_list.append({
            'course_name': row[0],
            'class_id': row[1],
            'credits': row[2],
            'tx1': row[3],
            'tx2': row[4],
            'giua_ky': row[5],
            'cuoi_ky': row[6],
            'diem_trung_binh': row[7],
            'created_at': row[8],
        })

    context = {
        'studentId': user_id,
        'username': username,
        'user_role': 'STUDENT',
        'grades_list': grades_list
    }

    return render(request, 'quanlydiem/grades.html', context)

# 3. View Dashboard (Thêm cái này để nút Sidebar hoạt động)
def teacher_grade_dashboard(request):
    # lấy tên giảng viên
    user_id = request.session.get('userId')
    print("DEBUG userId =", request.session.get('userId'))
    if not user_id:
        return redirect('login')
    username = fetch_teachername(user_id)

    current_teacher_id = 'T001' 

    classes = Classes.objects.filter(teacher__teacherId=current_teacher_id).select_related('courseId')
    
    return render(request, 'quanlydiem/teacher_dashboard.html', {'classes': classes, 'username': username})