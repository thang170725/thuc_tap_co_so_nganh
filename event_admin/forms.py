# event_admin/forms.py
from django import forms
from .models import Events

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        # Bảng 'Events' của bạn có id, title, time, receiver, created_at
        # Chúng ta chỉ cho admin sửa 3 trường này
        fields = ['title', 'time', 'receiver']
        
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Tiêu đề sự kiện'}
            ),
            'time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M' # Format chuẩn cho HTML5
            ),
            'receiver': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }
        
        labels = {
            'title': 'Tiêu đề',
            'time': 'Thời gian diễn ra',
            'receiver': 'Đối tượng thông báo',
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.time:
            # Chuyển đổi format DateTime của Python sang format của <input>
            self.initial['time'] = self.instance.time.strftime('%Y-%m-%dT%H:%M')