from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_grade_dashboard, name='teacher_grade_dashboard'),

    # Đường dẫn cho giảng viên nhập điểm (ví dụ: /grades/input/CL001/)
    path('input/<str:class_id>/', views.teacher_input_grades, name='teacher_input_grades'),
    
    # Đường dẫn cho sinh viên xem điểm
    path('my-grades/', views.student_my_grades, name='student_my_grades'),
]