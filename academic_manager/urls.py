from django.urls import path
from . import views

urlpatterns = [
    # 1. Trang danh sách Môn học (Read)
    path('courses/', views.course_list, name='course_list'),
    
    # 2. Trang tạo Môn học (Create)
    path('courses/create/', views.course_create_edit, name='course_create'),
    
    # 3. Trang chỉnh sửa Môn học (Update)
    path('courses/edit/<str:course_id>/', views.course_create_edit, name='course_edit'),
    
    # 4. Trang xác nhận xóa Môn học (Delete)
    path('courses/delete/<str:course_id>/', views.course_delete, name='course_delete'),
    
    # (Chúng ta sẽ thêm URL cho 'Classes' ở đây sau)
     # --- PHẦN B: THÊM CÁC URL QUẢN LÝ LỚP HỌC ---
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create_edit, name='class_create'),
    path('classes/edit/<str:class_id>/', views.class_create_edit, name='class_edit'),
    path('classes/delete/<str:class_id>/', views.class_delete, name='class_delete'),
    # --- PHẦN C: THÊM URL NÀY ---
    # URL này sẽ có dạng: /admin/academics/classes/manage/CL01/
    path('classes/manage/<str:class_id>/', views.manage_class_students, name='manage_class_students'),
]