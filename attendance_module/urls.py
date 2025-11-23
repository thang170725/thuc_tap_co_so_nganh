# attendance_module/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Trang danh sách lớp (Trang chủ của attendance)
    path('', views.teacher_class_list, name='teacher_class_list'),

    # !!! QUAN TRỌNG: Đưa dòng 'success' lên TRƯỚC dòng 'class_id' !!!
    # Django cần kiểm tra xem có phải là trang success không trước khi kiểm tra mã lớp
    path('success/', views.attendance_success, name='attendance_success'),
    
    # 2. Trang điểm danh chi tiết (Dynamic URL)
    # Vì <str:class_id> bắt tất cả các chuỗi ký tự, nó phải nằm ở cuối cùng (hoặc sau các đường dẫn tĩnh)
    path('<str:class_id>/', views.teacher_attendance_view, name='teacher_attendance'),
]