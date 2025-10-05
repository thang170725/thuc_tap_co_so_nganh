from myapp.models import Student
from django.contrib.auth.hashers import check_password

# Giả sử dữ liệu đã có trong database, không tạo mới
input_studentId = "SV001"
input_password = "123456"

try:
    student = Student.objects.get(studentId=input_studentId)
    if check_password(input_password, student.password):
        print("Đăng nhập thành công!")
    else:
        print("Sai mật khẩu")
except Student.DoesNotExist:
    print("Không tìm thấy studentId")
