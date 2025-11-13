from django import forms
from myapp.models import Courses, Teachers, Classes

class CourseForm(forms.ModelForm):
    # Dùng ModelChoiceField để tạo dropdown chọn Giảng viên
    teacherId = forms.ModelChoiceField(
        queryset=Teachers.objects.all(),
        label="Giảng viên phụ trách",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Courses
        fields = ['courseId', 'courseName', 'credits', 'descriptions', 'teacherId']
        labels = {
            'courseId': 'Mã Môn học',
            'courseName': 'Tên Môn học',
            'credits': 'Số tín chỉ',
            'descriptions': 'Mô tả môn học',
        }
        widgets = {
            'courseId': forms.TextInput(attrs={'class': 'form-control'}),
            'courseName': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'descriptions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    # --- THÊM FORM MỚI CHO LỚP HỌC (CLASSES) ---
class ClassForm(forms.ModelForm):
    # Model Classes của bạn có:
    # classId (Mã lớp)
    # courseId (FK - Môn học)
    # teacher (FK - Giảng viên, tên field là 'teacher' trong model)
    # semester (Học kỳ)
    
    # Tạo dropdown để chọn Môn học (từ Phần A)
    courseId = forms.ModelChoiceField(
        queryset=Courses.objects.all(),
        label="Môn học",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Tạo dropdown để chọn Giảng viên
    teacher = forms.ModelChoiceField(
        queryset=Teachers.objects.all(),
        label="Giảng viên dạy",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Classes
        fields = ['classId', 'courseId', 'teacher', 'semester']
        labels = {
            'classId': 'Mã Lớp (Ví dụ: IT1110.1)',
            'semester': 'Học kỳ (Ví dụ: HK1_2025)',
        }
        widgets = {
            'classId': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
        }