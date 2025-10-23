from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db import connection
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
from django.utils import timezone
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
'''
==============================================================
=================== VIEWS LOGIN CHUYÊN ROLE ==================
==============================================================
'''
def login_view(request):
  if request.method == "POST":
    username = request.POST.get('username') # lấy tài khoản trong trang login
    password = request.POST.get('password') # lấy mật khẩu trong trang login

    with connection.cursor() as cursor:
      cursor.execute(
        "SELECT userId, role FROM Users WHERE userId=%s AND passwordHash=%s", 
        [username, password]
      )
      row = cursor.fetchone()

    if row:
      user_id, role = row[0], row[1]
      # lưu userId vào session
      request.session['userId'] = user_id
      request.session['role'] = role
      if role == 'student':
        return redirect('student_home')
      elif role == 'teacher':
        return redirect('teacher_home')
      elif role == 'admin':
        return redirect('admin_home')
      else:
        messages.error(request, "Role không hợp lệ")
    else:
      messages.error(request, "Sai tài khoản hoặc mật khẩu")
  return render(request, "login.html")
'''
==============================================================
=================== VIEWS TRANG SINH VIÊN ====================
==============================================================
'''
# ================ VIEWS PHỤ TRANG SINH VIÊN =================
# hàm lấy tên của sinh viên đưa lên giao diện
def fetch_username(user_id):
  with connection.cursor() as cursor:
    cursor.execute('''
      select fullName
      from Students
      where studentId = %s 
    ''', [user_id])
    row = cursor.fetchone()
  return row[0] if row else None
# hàm lấy ra thời khóa biểu đưa lên trang sinh viên
def fetch_timetable(user_id):
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT c.courseId, c.courseName, t.fullName, sch.startTime, sch.endTime, sch.dayOfWeek, r.roomId
      FROM Students s
      JOIN Students_Courses sc ON s.studentId = sc.studentId
      JOIN Courses c ON sc.courseId = c.courseId
      JOIN Teachers t ON c.teacherId = t.teacherId
      JOIN Schedules sch ON c.courseId = sch.courseId
      JOIN Rooms r ON sch.roomId = r.roomId
      where s.studentId = %s
      ORDER BY s.studentId;
    """, [user_id])
    rows = cursor.fetchall()
  # gom nhóm theo thứ
  timetable = defaultdict(list)
  for courseId, courseName, teacherName, startTime, endTime, dayOfWeek, roomId in rows:
    timetable[dayOfWeek].append({
      "courseId": courseId,
      "courseName": courseName,
      "teacher": teacherName,
      "start": str(startTime),
      "end": str(endTime),
      "room": roomId,
    })   
  # Tạo khung 7 ngày (Mon → Sun)
  days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return {day: timetable.get(day, []) for day in days}
# =================== HÀM GỬI RESPONSE ĐẾN TRANG SINH VIÊN ===================

# hàm lấy chi tiết môn học đưa lên giao diện
def course_detail_api(request, course_id):
  try:
    with connection.cursor() as cursor:
      cursor.execute('''
        SELECT courseId, courseName, credits, descriptions
        FROM Courses
        WHERE courseId = %s
      ''', [course_id])
      row = cursor.fetchone()            
      if not row:
        return JsonResponse({"error": "Không tìm thấy môn học này"}, status=404)           
      course = {
        "courseId": row[0],
        "courseName": row[1],
        "credits": row[2],
        "descriptions": row[3],
      }
      return JsonResponse(course)
  except Exception as e:
    return JsonResponse({"error": str(e)}, status=500)

# lấy chi tiết thông tin sinh viên đưa lên trang sinh viên
def student__infor_detail_api(request, student_id):
  try:
    with connection.cursor() as cursor:
      cursor.execute('''
        SELECT studentId, fullName, major, className
        FROM Students
        WHERE studentId = %s
      ''', [student_id])
      row = cursor.fetchone()            
      if not row:
        return JsonResponse({"error": "Không tìm thấy thông tin sinh viên này"}, status=404)           
      student = {
        "studentId": row[0],
        "fullName": row[1],
        "major": row[2],
        "className": row[3],
      }
      return JsonResponse(student)
  except Exception as e:
    return JsonResponse({"error": str(e)}, status=500)
# ======================== VIEW CHÍNH TRANG SINH VIÊN ========================
def student_home(request):
  user_id = request.session.get('userId')
  if not user_id:
    return redirect('login')
  # gọi hàm phụ
  username = fetch_username(user_id)
  context = {
    'studentId': user_id,
    'username': username,
    'user_role': 'STUDENT'
  }
  return render(request, "student_home.html", context)

def timetable_api(request):
  student_id = request.session.get('userId')
  timetable = fetch_timetable(student_id)
  return JsonResponse(timetable)


def student_home_view(request):
  template = loader.get_template('student_home.html')
  return HttpResponse(template.render())


'''
==============================================================
=================== VIEWS TRANG GIẢNG VIÊN ===================
==============================================================
'''
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

def fetch_timetable_teacher(user_id):
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT c.courseId, c.courseName, sch.startTime, sch.endTime, sch.dayOfWeek, r.roomId, r.capacity
      FROM Teachers t
      JOIN Courses c ON t.teacherId = c.teacherId
      JOIN Schedules sch ON c.courseId = sch.courseId
      JOIN Rooms r ON sch.roomId = r.roomId
      where t.teacherId = %s
      ORDER BY t.teacherId;
    """, [user_id])
    rows = cursor.fetchall()
  # gom nhóm theo thứ
  timetable = defaultdict(list)
  for courseId, courseName, startTime, endTime, dayOfWeek, roomId, capacity in rows:
    timetable[dayOfWeek].append({
      "courseId": courseId,
      "courseName": courseName,
      "start": str(startTime),
      "end": str(endTime),
      "dayOfWeek": dayOfWeek,
      "room": roomId,
      "capacity": capacity
    })   
  # Tạo khung 7 ngày (Mon → Sun)
  days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return {day: timetable.get(day, []) for day in days}

def send_announcement(request): # gửi thông báo từ giảng viên tới học sinh
    if request.method != "POST":
        return JsonResponse({"error": "Chỉ hỗ trợ POST"}, status=405)

    sender_id = request.session.get("userId")
    course_id = request.POST.get("courseId")
    title = request.POST.get("title")
    content = request.POST.get("content")

    if not all([course_id, title, content]):
        return JsonResponse({"error": "Thiếu dữ liệu cần thiết"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Announcements (senderId, courseId, title, content, createdAt)
                VALUES (%s, %s, %s, %s, %s)
            """, [sender_id, course_id, title, content, timezone.now()])

        return JsonResponse({"message": "Đã gửi thông báo thành công!"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
'''
==============================================================
======== HÀM GỬI RESPONSE ĐẾN TRANG GIẢNG VIÊN ===============
==============================================================
'''
def timetable_teacher_api(request):
  teacher_id = request.session.get('userId')
  timetable = fetch_timetable_teacher(teacher_id)
  return JsonResponse(timetable)
# =================================== VIEW CHÍNH TRANG GIẢNG VIÊN ===================================
def teacher_home(request):
  user_id = request.session.get('userId')
  if not user_id:
    return redirect('login')
  # gọi hàm phụ
  username = fetch_teachername(user_id)
  # timetable = fetch_timetable_teacher(user_id)
  context = {
    'username': username,
    'user_role': 'TEACHER'
  }
  return render(request, "teacher_home.html", context)

# ================================================ API trả danh sách thông báo ================================================ 
def announcements_api(request):
  user_id = request.session.get('userId') # lấy user hiện tại
  if not user_id:
    return JsonResponse({'error': 'chưa đăng nhập'}, status=403)
  
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT a.title, a.content, a.createdAt, t.fullName AS senderName
      FROM Announcements a
      JOIN Courses c ON a.courseId = c.courseId
      join Teachers t on c.teacherId = t.teacherId
      JOIN Students_Courses sc ON c.courseId = sc.courseId
      JOIN Students s ON sc.studentId = s.studentId
      WHERE sc.studentId = %s
      ORDER BY a.createdAt DESC
    """, [user_id])
    rows = cursor.fetchall()

  announcements = []
  for title, content, createdAt, senderName in rows:
    announcements.append({
      "title": title,
      "content": content,
      "createdAt": createdAt.strftime("%Y-%m-%d %H:%M:%S"),
      "senderName": senderName,
    })

  return JsonResponse({"announcements": announcements})

def api_reminders(request):
    student_id = request.session.get("userId")
    if not student_id:
        return JsonResponse({"error": "Chưa đăng nhập"}, status=401)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.courseName, sch.startTime, sch.dayOfWeek, r.roomId
            FROM Students s
            JOIN Students_Courses sc ON s.studentId = sc.studentId
            JOIN Courses c ON sc.courseId = c.courseId
            JOIN Schedules sch ON c.courseId = sch.courseId
            JOIN Rooms r ON sch.roomId = r.roomId
            WHERE s.studentId = %s
        """, [student_id])
        schedules = cursor.fetchall()
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(vn_tz)
    today = now.strftime("%a")
    reminders = []
    for course_name, start_time, day_of_week, room_id in schedules:
        if day_of_week == today:
            class_time = datetime.combine(now.date(), start_time)
            if timezone.is_naive(class_time):
                class_time = timezone.make_aware(class_time, vn_tz)
            diff = class_time - now
            if timedelta(minutes=0) < diff <= timedelta(minutes=15):
                reminders.append({
                    "title": f"Sắp đến giờ học {course_name}",
                    "content": f"Học tại phòng {room_id} lúc {start_time.strftime('%H:%M')}.",
                    "createdAt": now.strftime("%Y-%m-%d %H:%M"),
                    "senderName": "Hệ thống"
                })

    return JsonResponse({"reminders": reminders})
'''
==============================================================
============ TRANG SINH VIÊN VÀ GIẢNG VIÊN XEM THÔNG BÁO =====
==============================================================
'''
@csrf_exempt
def get_events_api(request):
    """Trang sinh viên và giảng viên xem thông báo"""
    try:
        user_role = request.GET.get("role", "ALL")  # STUDENT, TEACHER, ALL
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT title, time
                FROM Events
                WHERE receiver = 'ALL' OR receiver = %s
                ORDER BY time DESC
                LIMIT 10
            """, [user_role])
            rows = cursor.fetchall()

        events = [
            {"title": r[0], "time": r[1].isoformat()}
            for r in rows
        ]
        return JsonResponse({"events": events})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

'''
==============================================================
===================== VIEWS TRANG ADMIN ======================
==============================================================
'''
# ====================== VIEWS PHỤ ===========================
def fetch_admin_name(user_id): # trả về  tên của admin
  with connection.cursor() as cursor:
    cursor.execute('''
      select fullName from Admins where adminId = %s 
    ''', [user_id])
    row = cursor.fetchone()
  return row[0] if row else None
'''
==============================================================
============== HÀM GỬI RESPONSE ĐẾN TRANG ADMIN ==============
==============================================================
'''
def admin_course_detail_api(request, course_id):
  try:
    with connection.cursor() as cursor:
      # lấy thông tin SINH VIÊN THEO LỚP HỌC
      cursor.execute('''
        SELECT 
          c.courseId,
          c.courseName,
          cl.classId,
          t.fullName AS teacherName,
          s.studentId,
          s.fullName AS studentName,
          s.major,
          s.className
        FROM Courses c
        JOIN Classes cl ON c.courseId = cl.courseId
        JOIN Teachers t ON cl.teacherId = t.teacherId
        JOIN Students_Classes sc ON cl.classId = sc.classId
        JOIN Students s ON sc.studentId = s.studentId
        WHERE c.courseId = %s;
      ''', [course_id])
      rows = cursor.fetchall()
      if not rows:
        return JsonResponse({"error": "Không tìm thấy môn học này."}, status=404)
      # lấy thông tin
      first_row = rows[0]
      course_id, course_name, class_id, teacher_name = first_row[0], first_row[1], first_row[2], first_row[3],
      students = [{
        "studentId": row[4],
        "fullName": row[5],
        "major": row[6],
        "className": row[7],
      }
      for row in rows
      ]
    return JsonResponse({
      "courseId": course_id,
      "courseName": course_name,
      "classId": class_id,
      "teacherName": teacher_name,
      "students": students,
    })
  
  except Exception as e:
    return JsonResponse({"error": str(e)}, status=500)
'''
==============================================================
========== TRẢ VỀ THÔNG TIN GIẢNG VIÊN THEO KHOA =============
==============================================================
'''
def department_teacher_api(request, department):
  try:
    with connection.cursor() as cursor:
      # lấy thông tin GV THEO KHOA
      cursor.execute('''
        select t.teacherId, t.fullName, u.email 
          from Teachers t
          join Users u on t.teacherId = u.userId
          WHERE LOWER(t.department) = LOWER(%s);
      ''', [department])
      rows = cursor.fetchall()
      if not rows:
        return JsonResponse({"error": "Không tìm thấy thông tin khoa này."}, status=404)
      # lưu thông tin vào biến để gửi lên js
      teachers = [{
        "teacherId": row[0],
        "fullName": row[1],
        "email": row[2],
      }
      for row in rows
      ]
    return JsonResponse({
      "department": department,
      "teachers": teachers,
    })
  
  except Exception as e:
    return JsonResponse({"error": str(e)}, status=500)
'''
================================================================================
========== ADMIN GỬI THÔNG BÁO SỰ KIỆN CHO SINH VIÊN VÀ GIẢNG VIÊN =============
================================================================================
'''
@csrf_exempt  # 👈 thêm dòng này để tránh lỗi 403
def admin_event_api(request):
    """Admin gửi thông báo sự kiện"""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            title = data.get("title")
            time = data.get("time")
            receiver = data.get("receiver", "ALL")

            if not title or not time:
                return JsonResponse({"error": "Thiếu tiêu đề hoặc thời gian."}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Events (title, time, receiver)
                    VALUES (%s, %s, %s)
                """, [title, time, receiver])

            return JsonResponse({"message": "Gửi thông báo thành công!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)
'''
==============================================================
=============== VIEWS CHÍNH TRANG ADMIN ======================
==============================================================
'''
def admin_home(request):
  user_id = request.session.get('userId')
  if not user_id:
    return redirect('login')
  username = fetch_admin_name(user_id)
  # timetable = fetch_timetable_teacher(user_id)
  context = {
    'username': username,
    # 'timetable': timetable
  }
  return render(request, "admin_home.html", context)

def admin_teacher_infor(request):
    return render(request, 'admin_teacher_infor.html')

def admin_student_infor(request):
    return render(request, 'admin_student_infor.html')

