from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path("student_home/", views.student_home, name="student_home"),
    path("teacher_home/", views.teacher_home, name="teacher_home"),
    # đường dẫn trang giảng viên
    path("api/export_timetable/", views.export_timetable_pdf, name="export_timetable"),
    path("api/weather/", views.api_weather, name="api_weather"),
    path("api/timetable/", views.timetable_api, name="timetable_api"),
    path("api/timetable_teacher/", views.timetable_teacher_api, name="timetable_teacher_api"),
    path('api/announcements/', views.announcements_api, name='announcements_api'),
    path('api/reminders/', views.api_reminders, name='api_reminder'),
    path("api/send_announcement/", views.send_announcement, name="send_announcement"),  
    path('api/course-detail/<str:course_id>/', views.course_detail_api, name='course_detail_api'),
    path('api/student-infor-detail/<str:student_id>/', views.student__infor_detail_api, name='student_infor_detail_api'),
    path("api/events/", views.get_events_api, name="get_events_api"),
    # đường dẫn trang admin
    path("admin_home/", views.admin_home, name="admin_home"),
    path('admin_home/teacher-infor/', views.admin_teacher_infor, name='admin_teacher_infor'),
    path('admin_home/student-infor/', views.admin_student_infor, name='admin_student_infor'),
    path("api/admin_course_detail/<str:course_id>/", views.admin_course_detail_api, name="admin_course_detail_api"),
    path("api/department_teacher/<str:department>/", views.department_teacher_api, name="department_teacher_api"),
    path("api/admin_event/", views.admin_event_api, name="admin_event_api"),
    path('profile/', views.profile_management, name='profile_management'),
    path('password_change/', views.custom_password_change, name='custom_password_change'),
    path('logout/', views.custom_logout_view, name='custom_logout'),
    path('api/chat_ai/', views.chat_ai_api, name='chat_ai_api'),
]