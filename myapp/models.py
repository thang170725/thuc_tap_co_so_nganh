# myapp/models.py
from django.db import models

class User(models.Model):
    userId = models.CharField(max_length=20, primary_key=True)
    passwordHash = models.CharField(max_length=128)
    email = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)

class Student(models.Model):
    studentId = models.CharField(max_length=20, primary_key=True)
    userId = models.CharField(max_length=20)  # Chỉ lưu userId, không cần ForeignKey
    fullNameStudent = models.CharField(max_length=100, blank=True, null=True)
