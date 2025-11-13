from django import forms
from myapp.models import Rooms, Classes, Schedules, Students
from django.db.models import Q # <-- THÊM DÒNG NÀY VÀO

class RoomForm(forms.ModelForm):
    class Meta:
        model = Rooms
        # Model Rooms của bạn có: roomId, roomNumber, capacity, building
        fields = ['roomId', 'roomNumber', 'capacity', 'building']
        labels = {
            'roomId': 'Mã Phòng (ví dụ: A7_304)',
            'roomNumber': 'Tên Phòng (ví dụ: 304)',
            'capacity': 'Sức chứa',
            'building': 'Tòa nhà (ví dụ: A7)',
        }
        widgets = {
            'roomId': forms.TextInput(attrs={'class': 'form-control'}),
            'roomNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'building': forms.TextInput(attrs={'class': 'form-control'}),
        }
# --- THÊM FORM MỚI CHO XẾP LỊCH (SCHEDULES) ---
class ScheduleForm(forms.ModelForm):
    
    class Meta:
        model = Schedules
        # Model Schedules của bạn có: scheduleId, classId, roomId, 
        # startTime, endTime, dayOfWeek, weekNumber
        
        fields = ['scheduleId', 'classId', 'roomId', 'dayOfWeek', 
                  'startTime', 'endTime', 'weekNumber']
        labels = {
            'scheduleId': 'Mã Lịch học (Tùy chọn, ví dụ: SCH001)',
            'classId': 'Lớp học (Đã gán GV & SV)',
            'roomId': 'Phòng học',
            'dayOfWeek': 'Thứ trong tuần',
            'startTime': 'Giờ bắt đầu',
            'endTime': 'Giờ kết thúc',
            'weekNumber': 'Tuần học số',
        }
        widgets = {
            'scheduleId': forms.TextInput(attrs={'class': 'form-control'}),
            'classId': forms.Select(attrs={'class': 'form-select'}),
            'roomId': forms.Select(attrs={'class': 'form-select'}),
            'dayOfWeek': forms.Select(attrs={'class': 'form-select'}),
            'startTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'endTime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'weekNumber': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """
        Đây là nơi chứa toàn bộ logic CHỐNG TRÙNG LẶP
        """
        cleaned_data = super().clean()
        
        class_id = cleaned_data.get('classId')
        room_id = cleaned_data.get('roomId')
        day = cleaned_data.get('dayOfWeek')
        start_time = cleaned_data.get('startTime')
        end_time = cleaned_data.get('endTime')
        week = cleaned_data.get('weekNumber')
        
        # Lấy scheduleId (để loại trừ chính nó khi Sửa)
        current_schedule_id = self.instance.pk

        if not all([class_id, room_id, day, start_time, end_time, week]):
            # Nếu thiếu 1 trong các trường, bỏ qua
            return cleaned_data

        # 0. Kiểm tra thời gian hợp lệ
        if start_time >= end_time:
            self.add_error('endTime', 'Giờ kết thúc phải sau Giờ bắt đầu.')
            return cleaned_data

        # Logic kiểm tra thời gian chéo (overlap)
        # (Một lịch học BẮT ĐẦU < giờ KẾT THÚC của lịch mới)
        # VÀ (Một lịch học KẾT THÚC > giờ BẮT ĐẦU của lịch mới)
        overlap_query = (
            Q(startTime__lt=end_time) & Q(endTime__gt=start_time) &
            Q(dayOfWeek=day) & Q(weekNumber=week)
        )
        
        # Loại trừ chính lịch học này (nếu đang Sửa)
        conflicts = Schedules.objects.filter(overlap_query).exclude(scheduleId=current_schedule_id)
        
        # --- 1. KIỂM TRA TRÙNG LỊCH PHÒNG ---
        room_conflict = conflicts.filter(roomId=room_id)
        if room_conflict.exists():
            conflict = room_conflict.first()
            self.add_error('roomId', f"Lỗi: Phòng {room_id} đã bị trùng lịch "
                                   f"với Lớp {conflict.classId.classId} "
                                   f"(từ {conflict.startTime} - {conflict.endTime}).")

        # --- 2. KIỂM TRA TRÙNG LỊCH GIẢNG VIÊN ---
        teacher = class_id.teacher
        teacher_conflict = conflicts.filter(classId__teacher=teacher)
        if teacher_conflict.exists():
            conflict = teacher_conflict.first()
            self.add_error('classId', f"Lỗi: GV {teacher.fullName} đã bị trùng lịch "
                                    f"với Lớp {conflict.classId.classId} "
                                    f"(tại Phòng {conflict.roomId.roomId}).")
            
        # --- 3. KIỂM TRA TRÙNG LỊCH SINH VIÊN ---
        # (Lấy danh sách ID sinh viên của lớp đang xếp)
        students_in_class = class_id.students.all().values_list('studentId', flat=True)
        
        if students_in_class:
            # Tìm bất kỳ lịch học nào (conflicts) 
            # mà Lớp học của nó (classId)
            # có chứa (students__in) 
            # bất kỳ sinh viên nào (students_in_class)
            student_conflict = conflicts.filter(classId__students__in=students_in_class)
            
            if student_conflict.exists():
                conflict = student_conflict.first()
                # (Tìm 1 SV bị trùng để báo lỗi)
                conflicting_student = Students.objects.filter(
                    studentId__in=students_in_class,
                    joined_classes=conflict.classId
                ).first()
                
                self.add_error('classId', f"Lỗi: Sinh viên ({conflicting_student.fullName}...) "
                                        f"đã bị trùng lịch với Lớp {conflict.classId.classId} "
                                        f"(tại Phòng {conflict.roomId.roomId}).")