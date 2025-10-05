from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('login/', views.logins, name='login'),
    path('', views.login_view, name='login'),
    path("student_home/", views.student_home_view, name="student_home"),
    path("teacher_home/", views.teacher_home_view, name="teacher_home"),
]