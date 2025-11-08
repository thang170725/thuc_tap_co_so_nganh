from django.db import models

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

class Courses(models.Model):
    courseId = models.CharField(max_length=20, primary_key=True, blank=True)
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

class Students_Courses(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
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

class Rooms(models.Model):
    roomid = models.CharField(max_length=20, primary_key=True, blank=True)
    roomNumber = models.CharField(max_length=20, blank=True, null=True)
    capacity = models.IntegerField()
    building = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'Rooms'

class Schedules(models.Model):
    scheduleid = models.CharField(max_length=20, primary_key=True, blank=True)
    courseId = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        db_column='courseId',         
    )
    roomId = models.ForeignKey(
        Rooms,
        on_delete=models.CASCADE,
        db_column='roomId',         
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
        ('Sum', 'Sum')
    ]
    dayOfWeek = models.CharField(
        max_length=20, 
        choices=day_choices, 
        blank=True, 
        null=True
    )
    weekNumber = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'Schedules'

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
    semester = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'Classes'

    def __str__(self):
        return f"{self.classId} - {self.course} ({self.semester})"


class Announcements(models.Model):
    announcementId = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        'Users', 
        on_delete=models.CASCADE, 
        db_column='senderId'
    )
    senderRole = models.CharField(
        max_length=10,
        choices=[('teacher', 'Teacher'), ('admin', 'Admin')]
    )
    classId = models.ForeignKey(
        'Classes',
        on_delete=models.CASCADE, 
        db_column='classId'
    )
    courseId = models.ForeignKey(
        'Courses', 
        on_delete=models.CASCADE, 
        db_column='courseId'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Announcements'

    def __str__(self):
        return f"{self.title} ({self.senderRole})"
    
class Materials(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
# Bảng đang cân nhắc:
