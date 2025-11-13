from django.db import models

## 1. Bảng Users (Bảng 2)
# Đây là bảng gốc, các bảng Student, Teacher, Admin sẽ tham chiếu đến
class Users(models.Model):
    userId = models.CharField(max_length=20, primary_key=True)
    passwordHash = models.CharField(max_length=255)
    email = models.CharField(max_length=100, blank=True, null=True)
    role_choices = [
        ('admin', 'admin'),
        ('teacher', 'teacher'),
        ('student', 'student')
    ]
    role = models.CharField(
        max_length=20, 
        choices=role_choices, 
        blank=True, 
        null=True
    )

    class Meta:
        managed = False
        db_table = 'Users'

    def __str__(self):
        return self.userId

## 2. Bảng Students (Bảng 3)
class Students(models.Model):
    studentId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        db_column='studentId',   # cột trong bảng Students
        primary_key=True         # PK của Students
    )
    fullName = models.CharField(max_length=50, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    className = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Students'

## 3. Bảng Teachers (Bảng 4)
class Teachers(models.Model):
    teacherId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        db_column='teacherId',  
        primary_key=True 
    )
    fullName = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Teachers'

## 4. Bảng Admins (Bảng 5) - (ĐÃ THÊM)
# Model này bị thiếu, tôi đã thêm vào
class Admins(models.Model):
    adminId = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        db_column='adminId',   # cột trong bảng Admins
        primary_key=True       # PK của Admins
    )
    fullName = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Admins'

## 5. Bảng Courses (Bảng 6)
class Courses(models.Model):
    # SỬA LỖI: Đã xóa `blank=True`. Khóa chính không được rỗng.
    courseId = models.CharField(max_length=20, primary_key=True)
    courseName = models.CharField(max_length=100, blank=True, null=True)
    credits = models.IntegerField()
    descriptions = models.TextField()
    teacherId = models.ForeignKey(
        Teachers,
        on_delete=models.CASCADE,
        db_column='teacherId',         
    )

    class Meta:
        managed = False
        db_table = 'Courses'

## 6. Bảng Students_Courses (Bảng 7)
class Students_Courses(models.Model):
    # SỬA LỖI: Đã xóa `blank=True`. Khóa chính không được rỗng.
    id = models.AutoField(primary_key=True)
    studentId = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        db_column='studentId',         
    )
    courseId = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        db_column='courseId',         
    )

    class Meta:
        managed = False
        db_table = 'Students_Courses'

## 7. Bảng Rooms (Bảng 8)
class Rooms(models.Model):
    # SỬA LỖI: Đã xóa `blank=True`.
    # SỬA TÊN: Đổi `roomid` thành `roomId` cho nhất quán
    roomId = models.CharField(max_length=20, primary_key=True)
    roomNumber = models.CharField(max_length=20, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True) # Capacity có thể null
    building = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'Rooms'

# myapp/models.py

## 8. Bảng Schedules (Bảng 9) - (ĐÃ SỬA LỖI LOGIC)
class Schedules(models.Model):
    scheduleId = models.CharField(max_length=20, primary_key=True)
    
    # --- ĐÂY LÀ THAY ĐỔI QUAN TRỌNG ---
    # Nó phải liên kết với Bảng 10 (Classes), KHÔNG PHẢI Bảng 6 (Courses)
    classId = models.ForeignKey(
        'Classes', 
        on_delete=models.CASCADE, 
        db_column='classId',
        related_name='schedules' # Thêm related_name để query ngược
    )
    # -----------------------------------
    
    roomId = models.ForeignKey(
        Rooms,
        on_delete=models.CASCADE,
        db_column='roomId',
        related_name='schedules' # Thêm related_name
    )
    startTime = models.TimeField()
    endTime = models.TimeField()
    day_choices = [
        ('Mon', 'Mon'),
        ('Tue', 'Tue'),
        ('Wed', 'Wed'),
        ('Thu', 'Thu'),
        ('Fri', 'Fri'),
        ('Sat', 'Sat'),
        ('Sun', 'Sun') 
    ]
    dayOfWeek = models.CharField(
        max_length=20, 
        choices=day_choices, 
        blank=True, 
        null=True
    )
    weekNumber = models.IntegerField(default=1) # (Thêm default=1)
    
    class Meta:
        managed = False
        db_table = 'Schedules'
## 9. Bảng Classes (Bảng 10)
class Classes(models.Model):
    classId = models.CharField(primary_key=True, max_length=20)
    courseId = models.ForeignKey(
        'Courses', 
        on_delete=models.CASCADE, 
        db_column='courseId'
    )
    teacher = models.ForeignKey(
        'Teachers', 
        on_delete=models.CASCADE, 
        db_column='teacherId'
    )
    semester = models.CharField(max_length=20, blank=True, null=True) # Thêm blank/null
    students = models.ManyToManyField(
        Students,
        through='Students_Classes', # Tên model của bảng trung gian
        related_name='joined_classes'
    )
    class Meta:
        managed = False
        db_table = 'Classes'

    def __str__(self):
        # Sửa lỗi: Thay 'self.course' bằng 'self.courseId'
        # vì tên trường là 'courseId'
        return f"{self.classId} - {self.courseId} ({self.semester})"

## 10. Bảng Students_Classes (Bảng 11)
# (Bạn chưa có model này, nhưng nó cần thiết cho Bảng Classes)
# Nếu bạn không cần định nghĩa nó, Django sẽ tự tạo
# nhưng nếu bạn muốn rõ ràng, nó đây:
class Students_Classes(models.Model):
    id = models.AutoField(primary_key=True)
    studentId = models.ForeignKey(
        Students, 
        on_delete=models.CASCADE, 
        db_column='studentId'
    )
    classId = models.ForeignKey(
        Classes, 
        on_delete=models.CASCADE, 
        db_column='classId'
    )

    class Meta:
        managed = False
        db_table = 'Students_Classes'
        unique_together = (('studentId', 'classId'))


## 11. Bảng Announcements (Bảng 12)
class Announcements(models.Model):
    announcementId = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        'Users', 
        on_delete=models.CASCADE, 
        db_column='senderId'
    )
    senderRole = models.CharField(
        max_length=10,
        choices=[('teacher', 'Teacher'), ('admin', 'Admin')],
        blank=True, null=True # Thêm blank/null
    )
    classId = models.ForeignKey(
        'Classes',
        on_delete=models.CASCADE, 
        db_column='classId',
        blank=True, null=True # Thông báo chung có thể không có classId
    )
    courseId = models.ForeignKey(
        'Courses', 
        on_delete=models.CASCADE, 
        db_column='courseId',
        blank=True, null=True # Thông báo chung có thể không có courseId
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Announcements'

    def __str__(self):
        return f"{self.title} ({self.senderRole})"

## 12. Bảng Events (Bảng 13)
# (Cần cho chức năng Quản lý Sự kiện)
class Events(models.Model):
    id = models.AutoField(primary_key=True) # Sửa lỗi: Xóa blank=True
    title = models.CharField(max_length=255)
    time = models.DateTimeField()
    
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Events'
        ordering = ['-time']
        
    def __str__(self):
        return self.title