from django import forms
from myapp.models import Users # Import model từ app cũ

class UserCreateForm(forms.Form):
    userId = forms.CharField(label="Mã User (Tên đăng nhập)", max_length=20, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    password = forms.CharField(label="Mật khẩu", max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    fullName = forms.CharField(label="Họ và Tên", max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    email = forms.EmailField(label="Email", required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    role = forms.ChoiceField(label="Vai trò", choices=Users.role_choices, required=True,
                             widget=forms.Select(attrs={'class': 'form-select'}))

class UserEditForm(forms.Form):
    # Admin không nên sửa Tên đăng nhập (userId)
    fullName = forms.CharField(label="Họ và Tên", max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    email = forms.EmailField(label="Email", required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    role = forms.ChoiceField(label="Vai trò", choices=Users.role_choices, required=True,
                             widget=forms.Select(attrs={'class': 'form-select'}))
    
    # Lưu ý: Chúng ta không cho sửa vai trò phức tạp (vd: Student -> Teacher)
    # hoặc reset mật khẩu ở đây để giữ logic đơn giản.
    # User có thể tự đổi mật khẩu của họ.