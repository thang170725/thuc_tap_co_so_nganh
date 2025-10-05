from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
import mysql.connector

def logins(request):
    return render(request, "login.html")
# def logins(request):
#   template = loader.get_template('login.html')
#   return HttpResponse(template.render())

'''
tạo và test hàm đăng nhập có tương tác với cơ sở dữ liệu
'''
class MockRequest: # đây là lớp để test nhanh hàm đăng nhập
  def __init__(self, method, post_data=None):
    self.method = method
    self.POST = post_data or {}

def login_view(request):
  if request.method == "POST":
    username = request.POST.get('username') # biến lưu tài khoản đăng nhập
    password = request.POST.get('password') # biến lưu mật khẩu

    # Kết nối MySQL
    db = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="170725",
      database="MyDatabase"
      )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE userId=%s AND passwordHash=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
      role = user['role']
      if role == 'student':
        return redirect('student_home')
      elif role == 'teacher':
        return redirect('teacher_home')
      else:
        messages.error(request, "Role không hợp lệ")
    else:
      messages.error(request, "Sai tài khoản hoặc mật khẩu")
  return render(request, "login.html")

# if __name__ == "__main__":
#   # giả lập POST
#   fake_post = {'username': 'thang123', 'password': 'mypassword'}
#   request = MockRequest('POST', fake_post)
#   login_view(request=request)

'''
render trang chủ của student và teacher
'''
def student_home_view(request):
  template = loader.get_template('student_home.html')
  return HttpResponse(template.render())

def teacher_home_view(request):
  template = loader.get_template('teacher_home.html')
  return HttpResponse(template.render())