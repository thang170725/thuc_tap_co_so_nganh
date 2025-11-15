"""
URL configuration for thoi_khoa_bieu project.
"""
from django.contrib import admin
from django.urls import path, include
from myapp import views as myapp_views

# BỎ 'from myapp import views' đi, file này không cần nó

urlpatterns = [
    # Các URL của app admin (nên đặt trước)
    path('admin/users/', include('user_manager.urls')), 
    path('admin/events/', include('event_admin.urls')),
    path('admin/academics/', include('academic_manager.urls')),
    path('admin/scheduling/', include('schedule_manager.urls')),
    path('admin/', admin.site.urls),
    
    
    # Kích hoạt các link 'logout', 'password_change'
    
    # Dòng này sẽ bao gồm TẤT CẢ các URL
    # trong file myapp/urls.py mà bạn vừa gửi
    # (bao gồm 'profile/', 'login/', 'admin_home/'...)
    path('', include('myapp.urls')), 
    path('api/chat_ai/', myapp_views.chat_ai_api, name='chat_ai_api'),
]