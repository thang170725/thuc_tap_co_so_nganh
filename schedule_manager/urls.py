from django.urls import path
from . import views

urlpatterns = [
    # --- PHẦN A: QUẢN LÝ PHÒNG HỌC ---
    # 1. Trang danh sách Phòng học (Read)
    path('rooms/', views.room_list, name='room_list'),
    
    # 2. Trang tạo Phòng học (Create)
    path('rooms/create/', views.room_create_edit, name='room_create'),
    
    # 3. Trang chỉnh sửa Phòng học (Update)
    path('rooms/edit/<str:room_id>/', views.room_create_edit, name='room_edit'),
    
    # 4. Trang xác nhận xóa Phòng học (Delete)
    path('rooms/delete/<str:room_id>/', views.room_delete, name='room_delete'),
    
    # (Chúng ta sẽ thêm URL cho 'Schedules' ở đây sau)
    # --- PHẦN B: THÊM CÁC URL XẾP LỊCH TKB ---
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create_edit, name='schedule_create'),
    path('schedules/edit/<str:schedule_id>/', views.schedule_create_edit, name='schedule_edit'),
    path('schedules/delete/<str:schedule_id>/', views.schedule_delete, name='schedule_delete'),
]