from django.urls import path
from . import views

urlpatterns = [
    # 1. Trang danh sách (Read)
    path('', views.user_list, name='user_list'),
    
    # 2. Trang tạo user (Create)
    path('create/', views.user_create, name='user_create'),
    
    # 3. Trang chỉnh sửa (Update)
    path('edit/<str:user_id>/', views.user_edit, name='user_edit'),
    
    # 4. Trang xác nhận xóa (Delete)
    path('delete/<str:user_id>/', views.user_delete, name='user_delete'),
]