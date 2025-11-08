# myapp/forms.py
from django import forms

class ProfileUpdateForm(forms.Form):
    # (Form này của bạn đã đúng, giữ nguyên)
    email = forms.EmailField(
        label="Địa chỉ Email", 
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'style': 'width: 95%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;'})
    )
    fullName = forms.CharField(
        label="Họ và Tên", 
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 95%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;'})
    )

# --- THÊM FORM MỚI NÀY VÀO ---
# (Form này không dùng hệ thống auth của Django)
class CustomPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="Mật khẩu mới", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 95%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;'})
    )
    new_password2 = forms.CharField(
        label="Xác nhận mật khẩu", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 95%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    # Hàm kiểm tra xem 2 mật khẩu có khớp không
    def clean(self):
        cleaned_data = super().clean()
        np1 = cleaned_data.get("new_password1")
        np2 = cleaned_data.get("new_password2")
        if np1 and np2 and np1 != np2:
            raise forms.ValidationError("Hai mật khẩu không khớp.")
        return cleaned_data