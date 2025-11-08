# event_admin/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Tên 'event_management' dùng trong template
    path('', views.event_management, name='event_management'), 
    
    path('create/', views.event_create_update, name='event_create'),
    
    path('update/<int:event_id>/', 
         views.event_create_update, name='event_update'),
         
    path('delete/<int:event_id>/', 
         views.event_delete, name='event_delete'),
]