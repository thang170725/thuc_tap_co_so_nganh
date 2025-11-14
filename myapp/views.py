from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.template import loader
from django.db import connection
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
from django.utils import timezone
import json
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.font_manager as fm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import requests
'''
==============================================================
=================== VIEWS LOGIN CHUYÊN ROLE ==================
==============================================================
'''
# myapp/views.py
# ... (các import cũ của bạn) ...

# --- ĐẢM BẢO BẠN ĐÃ IMPORT NHỮNG THỨ NÀY ---
from django.db import connection
from django.contrib.auth import logout # (Vẫn dùng logout của Django để xóa session)
from .forms import ProfileUpdateForm, CustomPasswordChangeForm
from .models import Users, Students, Teachers, Admins
# -------------------------------------------


#
# --- 1. THAY THẾ HÀM NÀY ---
#
def profile_management(request):
    # Dùng hệ thống session của bạn
    user_id = request.session.get('userId')
    if not user_id:
        return redirect('login') 
    
    try:
        user_obj = Users.objects.get(userId=user_id)
    except Users.DoesNotExist:
        messages.error(request, 'Lỗi: Không tìm thấy hồ sơ người dùng.')
        return redirect('login') 

    profile_obj = None
    try:
        if user_obj.role == 'student':
            profile_obj = Students.objects.get(studentId=user_obj)
        elif user_obj.role == 'teacher':
            profile_obj = Teachers.objects.get(teacherId=user_obj)
        elif user_obj.role == 'admin':
            profile_obj = Admins.objects.get(adminId=user_obj)
    except (Students.DoesNotExist, Teachers.DoesNotExist, Admins.DoesNotExist):
        pass # Bỏ qua nếu không có (ví dụ: admin không có trong bảng Admins)

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST)
        if profile_form.is_valid():
            new_email = profile_form.cleaned_data['email']
            new_fullName = profile_form.cleaned_data['fullName']
            
            try:
                # Dùng raw SQL (giống login_view của bạn)
                with connection.cursor() as cursor:
                    # Cập nhật Bảng Users
                    cursor.execute(
                        "UPDATE Users SET email = %s WHERE userId = %s",
                        [new_email, user_id]
                    )
                    
                    # Cập nhật Bảng Students/Teachers/Admins
                    if profile_obj:
                        table_name = profile_obj._meta.db_table
                        id_field = profile_obj._meta.pk.name
                        cursor.execute(
                            f"UPDATE {table_name} SET fullName = %s WHERE {id_field} = %s",
                            [new_fullName, user_id]
                        )
                
                messages.success(request, 'Cập nhật thông tin thành công!')
                return redirect('profile_management')
            except Exception as e:
                messages.error(request, f'Lỗi cơ sở dữ liệu: {e}')
    else:
        # GET: Hiển thị thông tin hiện tại
        profile_form = ProfileUpdateForm(initial={
            'email': user_obj.email, 
            'fullName': profile_obj.fullName if profile_obj else ''
        })

    context = {
        'profile_form': profile_form,
        'user_profile': user_obj # Gửi user_profile để base.html hiển thị sidebar
    }
    return render(request, 'profile_management.html', context)

#
# --- 2. THAY THẾ HÀM NÀY ---
#
def custom_password_change(request):
    user_id = request.session.get('userId')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            
            try:
                # Dùng raw SQL (giống login_view của bạn)
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE Users SET passwordHash = %s WHERE userId = %s",
                        [new_password, user_id]
                    )
                
                logout(request) # Xóa session
                messages.success(request, 'Đổi mật khẩu thành công! Vui lòng đăng nhập lại.')
                return redirect('login') 
            except Exception as e:
                messages.error(request, f'Lỗi cơ sở dữ liệu: {e}')
        else:
            # Lỗi (ví dụ: 2 mật khẩu không khớp) sẽ được giữ lại trong 'form'
            messages.error(request, 'Đổi mật khẩu thất bại. Vui lòng kiểm tra lại.')
    else:
        form = CustomPasswordChangeForm()

    context = {
        'form': form,
        'user_profile': Users.objects.get(userId=user_id) # Gửi user_profile
    }
    return render(request, 'password_change.html', context)

#
# --- 3. THAY THẾ/THÊM HÀM NÀY ---
#
def custom_logout_view(request):
    logout(request) # Hàm này chỉ xóa session, rất an toàn
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')
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
# --- THAY THẾ TOÀN BỘ HÀM NÀY ---
#
# hàm lấy ra thời khóa biểu đưa lên trang sinh viên
def fetch_timetable(user_id):
  with connection.cursor() as cursor:
    
    # --- ĐÂY LÀ CÂU SQL ĐÃ SỬA LỖI ---
    # (Nó sẽ tìm TKB dựa trên Lớp học (Classes)
    # thay vì Môn học (Courses) như code cũ)
    cursor.execute("""
      SELECT 
          c.courseId, 
          c.courseName, 
          t.fullName, 
          sch.startTime, 
          sch.endTime, 
          sch.dayOfWeek, 
          r.roomId
      FROM Students s
      JOIN Students_Classes sc ON s.studentId = sc.studentId   -- (Từ SV -> Bảng 11)
      JOIN Classes cl ON sc.classId = cl.classId               -- (Bảng 11 -> Bảng 10 (Lớp))
      JOIN Schedules sch ON cl.classId = sch.classId           -- (Bảng 10 -> Bảng 9 (Lịch)) <-- SỬA LỖI Ở ĐÂY
      JOIN Courses c ON cl.courseId = c.courseId               -- (Bảng 10 -> Bảng 6 (Môn))
      JOIN Teachers t ON cl.teacherId = t.teacherId             -- (Bảng 10 -> Bảng 4 (GV))
      JOIN Rooms r ON sch.roomId = r.roomId                   -- (Bảng 9 -> Bảng 8 (Phòng))
      WHERE s.studentId = %s
      ORDER BY sch.startTime;
    """, [user_id])
    # --- KẾT THÚC CÂU SQL ĐÃ SỬA ---
    
    rows = cursor.fetchall()
    
  # (Phần code gom nhóm bên dưới đã đúng, giữ nguyên)
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
#
# --- KẾT THÚC HÀM CẦN THAY THẾ ---
#
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
      join Classes cl on c.courseId = cl.courseId
      JOIN Schedules sch ON cl.classId = sch.ClassId
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
            join Classes cl on c.courseId = cl.courseId
            JOIN Schedules sch ON cl.classId = sch.classId
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

def export_timetable_pdf(request):
    """Xuất thời khóa biểu giảng viên ra PDF"""
    user_id = request.session.get("userId")
    if not user_id:
        return JsonResponse({"error": "Bạn chưa đăng nhập"}, status=401)

    # --- Lấy dữ liệu thời khóa biểu ---
    data = fetch_timetable_teacher(user_id)  # Hàm của bạn

    # --- Buffer PDF ---
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    # --- Đăng ký font Unicode ---
    font_path = fm.findfont("DejaVu Sans")  # Ubuntu thường có sẵn
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    # --- Style ---
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'],
                                 fontName='DejaVuSans', alignment=TA_CENTER,
                                 fontSize=18, leading=22)
    day_style = ParagraphStyle('day', parent=styles['Heading2'],
                               fontName='DejaVuSans', fontSize=14,
                               spaceBefore=10, spaceAfter=5)
    text_style = ParagraphStyle('text', parent=styles['Normal'],
                                fontName='DejaVuSans', fontSize=12,
                                leading=16, alignment=TA_LEFT)

    # --- Nội dung PDF ---
    story = []
    story.append(Paragraph("THỜI KHÓA BIỂU GIẢNG VIÊN", title_style))
    story.append(Spacer(1, 12))

    for day, classes in data.items():
        story.append(Paragraph(f"📅 {day}", day_style))
        if not classes:
            story.append(Paragraph("Không có lớp", text_style))
            story.append(Spacer(1, 6))
            continue

        for c in classes:
            line = f"- {c['courseName']} ({c['start']} - {c['end']}) | Phòng: {c['room']} | Sĩ số: {c['capacity']}"
            story.append(Paragraph(line, text_style))
        story.append(Spacer(1, 8))

    # --- Build PDF ---
    doc.build(story)
    buffer.seek(0)
    filename = f"timetable_{user_id}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename, content_type='application/pdf')

def api_weather(request):
    city = request.GET.get("city", "Hà Nội")
    API_KEY = "a3502bbb398c639df116db612b1cdf2a"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},vn&appid={API_KEY}&units=metric&lang=vi"
    
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({"error": "Không thể lấy dữ liệu thời tiết"}, status=500)
    
    data = response.json()
    result = {
        "temp": data["main"]["temp"],
        "desc": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "city": city,
        "icon": data["weather"][0]["icon"]  # icon OpenWeather
    }
    return JsonResponse(result)