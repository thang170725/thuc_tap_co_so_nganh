# attendance_module/forms.py
from django import forms
from django.forms import modelformset_factory
from myapp.models import Attendances # Thay 'myapp' bằng tên App chứa Models thực tế của bạn

class AttendanceForm(forms.ModelForm):
    # Trường hiển thị tên sinh viên (chỉ để hiển thị, không lưu vào DB)
    full_name = forms.CharField(label="Họ và tên", required=False, disabled=True)
    
    class Meta:
        model = Attendances
        # Chỉ hiển thị các trường cần nhập liệu
        fields = ['studentId', 'status', 'note']
        widgets = {
            'studentId': forms.HiddenInput(), # Ẩn studentId để gửi ngầm
            # Chuyển sang RadioSelect để hiển thị dạng nút chọn
            'status': forms.RadioSelect(), 
            'note': forms.TextInput(attrs={'placeholder': 'Ghi chú...', 'class': 'note-input'}),
        }

# Sử dụng modelformset_factory để tạo Formset
AttendanceFormSet = modelformset_factory(
    Attendances,
    form=AttendanceForm,
    fields=['attendanceId', 'studentId', 'status', 'note'], # Thêm 'id' để cập nhật bản ghi cũ
    extra=0, # Không thêm dòng trống
    can_delete=False
)