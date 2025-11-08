# event_admin/models.py
from django.db import models

class Events(models.Model):
    # Django sẽ tự động dùng cột 'id' (AutoField) làm khóa chính
    # nếu bạn không chỉ định primary_key=True
    
    title = models.CharField(max_length=255, blank=False, null=False) # Sửa lại: NOT NULL
    time = models.DateTimeField(blank=False, null=False) # Sửa lại: NOT NULL
    
    RECEIVER_CHOICES = [
        ('ALL', 'Tất cả (ALL)'),
        ('STUDENT', 'Chỉ Sinh viên'),
        ('TEACHER', 'Chỉ Giảng viên'),
    ]
    receiver = models.CharField(
        max_length=10, 
        choices=RECEIVER_CHOICES, 
        default='ALL'
    )
    # Tên cột trong DB là 'created_at'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False # QUAN TRỌNG: Nói Django không quản lý (tạo/xóa) bảng này
        db_table = 'Events' # Chỉ định tên bảng đã có
        ordering = ['-time'] # Sắp xếp sự kiện mới nhất lên đầu
        
    def __str__(self):
        return self.title