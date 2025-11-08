-- 1️⃣ Tạo Database
DROP DATABASE IF EXISTS MyDatabase;
CREATE DATABASE MyDatabase
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
USE MyDatabase;

-- 2️⃣ Bảng Users
CREATE TABLE Users (
  userId VARCHAR(20) PRIMARY KEY,
  passwordHash VARCHAR(255),
  email VARCHAR(100),
  role ENUM('admin', 'teacher', 'student')
);

-- 3️⃣ Bảng Students
CREATE TABLE Students (
  studentId VARCHAR(20) PRIMARY KEY,
  fullName VARCHAR(50),
  major VARCHAR(100),
  className VARCHAR(100),
  CONSTRAINT fk_user_student FOREIGN KEY (studentId) REFERENCES Users(userId)
);

-- 4️⃣ Bảng Teachers
CREATE TABLE Teachers (
  teacherId VARCHAR(20) PRIMARY KEY,
  fullName VARCHAR(50),
  department VARCHAR(100),
  CONSTRAINT fk_user_teacher FOREIGN KEY (teacherId) REFERENCES Users(userId)
);

-- 5️⃣ Bảng Admins
CREATE TABLE Admins (
  adminId VARCHAR(20) PRIMARY KEY,
  fullName VARCHAR(50),
  CONSTRAINT fk_user_admin FOREIGN KEY (adminId) REFERENCES Users(userId)
);

-- 6️⃣ Bảng Courses
CREATE TABLE Courses (
  courseId VARCHAR(20) PRIMARY KEY,
  courseName VARCHAR(100),
  credits INT,
  descriptions TEXT,
  teacherId VARCHAR(20),
  CONSTRAINT fk_course_teacher FOREIGN KEY (teacherId) REFERENCES Teachers(teacherId)
);

-- 7️⃣ Bảng Students_Courses (liên kết SV - Môn học)
CREATE TABLE Students_Courses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  studentId VARCHAR(20),
  courseId VARCHAR(20),
  CONSTRAINT fk_sc_student FOREIGN KEY (studentId) REFERENCES Students(studentId),
  CONSTRAINT fk_sc_course FOREIGN KEY (courseId) REFERENCES Courses(courseId)
);

-- 8️⃣ Bảng Rooms
CREATE TABLE Rooms (
  roomId VARCHAR(20) PRIMARY KEY,
  roomNumber VARCHAR(20),
  capacity INT,
  building VARCHAR(20)
);

-- 9️⃣ Bảng Schedules (Thời khóa biểu)
CREATE TABLE Schedules (
  scheduleId VARCHAR(20) PRIMARY KEY,
  courseId VARCHAR(20),
  roomId VARCHAR(20),
  startTime TIME,
  endTime TIME,
  dayOfWeek ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
  weekNumber INT,
  CONSTRAINT fk_schedule_room FOREIGN KEY (roomId) REFERENCES Rooms(roomId),
  CONSTRAINT fk_schedule_course FOREIGN KEY (courseId) REFERENCES Courses(courseId)
);

-- 🔟 Bảng Classes (lớp học cụ thể của từng môn)
CREATE TABLE Classes (
  classId VARCHAR(20) PRIMARY KEY,
  courseId VARCHAR(20),
  teacherId VARCHAR(20),
  semester VARCHAR(20),
  CONSTRAINT fk_class_course FOREIGN KEY (courseId) REFERENCES Courses(courseId),
  CONSTRAINT fk_class_teacher FOREIGN KEY (teacherId) REFERENCES Teachers(teacherId)
);

-- 11️⃣ Bảng Students_Classes (liên kết SV - Lớp học)
CREATE TABLE Students_Classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  studentId VARCHAR(20),
  classId VARCHAR(20),
  FOREIGN KEY (studentId) REFERENCES Students(studentId),
  FOREIGN KEY (classId) REFERENCES Classes(classId)
);

-- 12️⃣ Bảng Announcements (Thông báo)
CREATE TABLE Announcements (
  announcementId INT AUTO_INCREMENT PRIMARY KEY,
  senderId VARCHAR(20),
  senderRole ENUM('teacher', 'admin'),
  classId VARCHAR(20),
  courseId VARCHAR(20),
  title VARCHAR(255),
  content TEXT,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (senderId) REFERENCES Users(userId),
  FOREIGN KEY (courseId) REFERENCES Courses(courseId),
  FOREIGN KEY (classId) REFERENCES Classes(classId)
);

-- 13️⃣ Bảng Events (Sự kiện chung)
CREATE TABLE Events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  time DATETIME NOT NULL,
  receiver ENUM('ALL', 'STUDENT', 'TEACHER') DEFAULT 'ALL',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ✅ DỮ LIỆU MẪU THỰC TẾ

-- Users
INSERT INTO Users (userId, passwordHash, email, role) VALUES
('admin001', 'hash1', 'admin@school.edu.vn', 'admin'),
('gv2023600455', 'hash2', 'thay.hung@school.edu.vn', 'teacher'),
('gv2023600456', 'hash3', 'co.tram@school.edu.vn', 'teacher'),
('2023600455', 'hash4', 'ductuong@school.edu.vn', 'student'),
('2023600456', 'hash5', 'minhthuan@school.edu.vn', 'student'),
('2023600457', 'hash6', 'linhpham@school.edu.vn', 'student');

-- Admins
INSERT INTO Admins (adminId, fullName) VALUES
('admin001', 'Nguyễn Văn Nam');

-- Teachers
INSERT INTO Teachers (teacherId, fullName, department) VALUES
('gv2023600455', 'Thầy Nguyễn Văn Hùng', 'Công Nghệ Thông Tin'),
('gv2023600456', 'Cô Trần Thị Trâm', 'Toán - Tin');

-- Students
INSERT INTO Students (studentId, fullName, major, className) VALUES
('2023600455', 'Lê Đức Tường', 'An toàn thông tin', 'IT2A'),
('2023600456', 'Nguyễn Minh Thuận', 'Khoa học máy tính', 'IT2B'),
('2023600457', 'Phạm Ngọc Linh', 'Kỹ thuật phần mềm', 'IT2A');

-- Courses
INSERT INTO Courses (courseId, courseName, credits, descriptions, teacherId) VALUES
('C001', 'Toán Cao Cấp', 3, 'Môn học nền tảng về giải tích, đạo hàm, tích phân, đại số tuyến tính.', 'gv2023600456'),
('C002', 'Cơ Sở Dữ Liệu', 3, 'Học về thiết kế, tối ưu, truy vấn và quản lý cơ sở dữ liệu.', 'gv2023600455'),
('C003', 'Trí Tuệ Nhân Tạo', 3, 'Giới thiệu về AI, machine learning, và ứng dụng thực tế.', 'gv2023600455');

-- Students_Courses
INSERT INTO Students_Courses (studentId, courseId) VALUES
('2023600455', 'C001'),
('2023600455', 'C002'),
('2023600456', 'C002'),
('2023600457', 'C003');

-- Rooms
INSERT INTO Rooms (roomId, roomNumber, capacity, building) VALUES
('A7_304', '304', 75, 'A7'),
('B5_102', '102', 60, 'B5');

-- Schedules
INSERT INTO Schedules (scheduleId, courseId, roomId, startTime, endTime, dayOfWeek, weekNumber) VALUES
('SCH001', 'C001', 'A7_304', '07:30:00', '09:30:00', 'Mon', 1),
('SCH002', 'C002', 'B5_102', '09:45:00', '11:45:00', 'Wed', 1),
('SCH003', 'C003', 'A7_304', '13:00:00', '15:00:00', 'Fri', 1);

-- Classes
INSERT INTO Classes (classId, courseId, teacherId, semester) VALUES
('CL01', 'C002', 'gv2023600455', 'HK1_2025'),
('CL02', 'C001', 'gv2023600456', 'HK1_2025'),
('CL03', 'C003', 'gv2023600455', 'HK1_2025');

-- Students_Classes
INSERT INTO Students_Classes (studentId, classId) VALUES
('2023600455', 'CL01'),
('2023600455', 'CL02'),
('2023600456', 'CL01'),
('2023600457', 'CL03');

-- Announcements
INSERT INTO Announcements (senderId, senderRole, classId, courseId, title, content)
VALUES
('gv2023600455', 'teacher', 'CL01', 'C002', 'Thông báo lịch thi CSDL', 'Lịch thi giữa kỳ Cơ sở dữ liệu diễn ra vào ngày 25/11, phòng A7_304.'),
('gv2023600456', 'teacher', 'CL02', 'C001', 'Bài tập lớn Toán cao cấp', 'Sinh viên nộp bài tập lớn số 2 trước ngày 30/11.'),
('admin001', 'admin', NULL, NULL, 'Thông báo nghỉ lễ', 'Toàn trường nghỉ lễ Quốc khánh từ 1-3/9.');

-- Events
INSERT INTO Events (title, time, receiver)
VALUES
('Khai giảng năm học 2025-2026', '2025-09-05 07:00:00', 'ALL'),
('Hội thảo AI & Security', '2025-11-10 08:30:00', 'STUDENT'),
('Họp giảng viên học kỳ I', '2025-10-30 14:00:00', 'TEACHER');
-- 🔹 Thêm giáo viên
INSERT INTO Users (userId, passwordHash, email, role) VALUES
('gv2023600457', 'hash7', 'thay.hoa@school.edu.vn', 'teacher'),
('gv2023600458', 'hash8', 'co.lan@school.edu.vn', 'teacher'),
('gv2023600459', 'hash9', 'thay.kien@school.edu.vn', 'teacher');

INSERT INTO Teachers (teacherId, fullName, department) VALUES
('gv2023600457', 'Thầy Nguyễn Đức Hòa', 'Mạng máy tính'),
('gv2023600458', 'Cô Lê Thanh Lan', 'Kỹ thuật phần mềm'),
('gv2023600459', 'Thầy Phạm Quốc Kiên', 'Hệ thống nhúng');

-- 🔹 Thêm sinh viên
INSERT INTO Users (userId, passwordHash, email, role) VALUES
('2023600458', 'hash10', 'trungkien@school.edu.vn', 'student'),
('2023600459', 'hash11', 'tuananh@school.edu.vn', 'student'),
('2023600460', 'hash12', 'hoanglam@school.edu.vn', 'student'),
('2023600461', 'hash13', 'thuhien@school.edu.vn', 'student'),
('2023600462', 'hash14', 'quangvinh@school.edu.vn', 'student');

INSERT INTO Students (studentId, fullName, major, className) VALUES
('2023600458', 'Nguyễn Trung Kiên', 'Khoa học máy tính', 'IT2B'),
('2023600459', 'Phạm Tuấn Anh', 'Công nghệ phần mềm', 'IT2C'),
('2023600460', 'Trần Hoàng Lâm', 'Kỹ thuật máy tính', 'IT2D'),
('2023600461', 'Ngô Thu Hiền', 'An toàn thông tin', 'IT2A'),
('2023600462', 'Đinh Quang Vinh', 'Hệ thống thông tin', 'IT2E');

-- 🔹 Thêm môn học mới
INSERT INTO Courses (courseId, courseName, credits, descriptions, teacherId) VALUES
('C004', 'Mạng máy tính', 3, 'Giới thiệu cấu trúc, giao thức và vận hành mạng LAN/WAN, TCP/IP.', 'gv2023600457'),
('C005', 'Phát triển phần mềm', 3, 'Môn học về quy trình phát triển, kiểm thử, triển khai phần mềm.', 'gv2023600458'),
('C006', 'Vi điều khiển và IoT', 3, 'Nghiên cứu cảm biến, lập trình nhúng, và kết nối IoT.', 'gv2023600459'),
('C007', 'Phân tích dữ liệu', 3, 'Ứng dụng Python và SQL để xử lý, phân tích dữ liệu thực tế.', 'gv2023600455');

-- 🔹 Thêm lớp học cho các môn mới
INSERT INTO Classes (classId, courseId, teacherId, semester) VALUES
('CL04', 'C004', 'gv2023600457', 'HK1_2025'),
('CL05', 'C005', 'gv2023600458', 'HK1_2025'),
('CL06', 'C006', 'gv2023600459', 'HK1_2025'),
('CL07', 'C007', 'gv2023600455', 'HK1_2025');

-- 🔹 Thêm sinh viên vào lớp học
INSERT INTO Students_Classes (studentId, classId) VALUES
('2023600458', 'CL04'),
('2023600459', 'CL04'),
('2023600460', 'CL05'),
('2023600455', 'CL05'),
('2023600461', 'CL06'),
('2023600462', 'CL06'),
('2023600457', 'CL07'),
('2023600460', 'CL07');

-- 🔹 Thêm phòng học
INSERT INTO Rooms (roomId, roomNumber, capacity, building) VALUES
('A7_201', '201', 50, 'A7'),
('B2_301', '301', 80, 'B2'),
('C1_102', '102', 60, 'C1');

-- 🔹 Lịch học cho các môn mới
INSERT INTO Schedules (scheduleId, courseId, roomId, startTime, endTime, dayOfWeek, weekNumber) VALUES
('SCH004', 'C004', 'A7_201', '07:30:00', '09:30:00', 'Tue', 2),
('SCH005', 'C005', 'B2_301', '13:00:00', '15:00:00', 'Thu', 2),
('SCH006', 'C006', 'C1_102', '09:45:00', '11:45:00', 'Wed', 2),
('SCH007', 'C007', 'A7_304', '15:15:00', '17:15:00', 'Fri', 2);

-- 🔹 Thêm thông báo mới
INSERT INTO Announcements (senderId, senderRole, classId, courseId, title, content)
VALUES
('gv2023600457', 'teacher', 'CL04', 'C004', 'Bài kiểm tra giữa kỳ', 'Giữa kỳ Mạng máy tính sẽ diễn ra vào ngày 5/12.'),
('gv2023600458', 'teacher', 'CL05', 'C005', 'Bài tập nhóm 1', 'Các nhóm hoàn thiện tài liệu đặc tả yêu cầu trước ngày 15/11.'),
('gv2023600459', 'teacher', 'CL06', 'C006', 'Demo dự án IoT', 'Tuần tới sẽ có buổi demo thiết bị IoT, chuẩn bị mạch và tài liệu.'),
('admin001', 'admin', NULL, NULL, 'Bảo trì hệ thống e-learning', 'Hệ thống e-learning bảo trì từ 00h-03h ngày 28/10.'),
('gv2023600455', 'teacher', 'CL07', 'C007', 'Báo cáo cuối kỳ', 'Sinh viên nộp file .ipynb và .pdf trước ngày 20/12.');

-- 🔹 Thêm sự kiện trường
INSERT INTO Events (title, time, receiver)
VALUES
('Ngày hội việc làm CNTT 2025', '2025-12-15 08:00:00', 'STUDENT'),
('Cuộc thi lập trình CodeWar 2025', '2025-11-20 09:00:00', 'ALL'),
('Buổi chia sẻ "AI trong đời sống"', '2025-11-25 14:00:00', 'ALL'),
('Workshop về Bảo mật Web', '2025-10-28 09:00:00', 'TEACHER'),
('Chung kết Hackathon Đại học Kỹ thuật', '2025-12-05 08:00:00', 'ALL');
-- Xóa dữ liệu cũ để tránh trùng khóa
DELETE FROM Students_Classes;

-- ✅ Phân bố thực tế hơn: mỗi SV học 3-4 lớp, mỗi lớp có 4-5 SV

INSERT INTO Students_Classes (studentId, classId) VALUES
-- Lớp CL01: Cơ Sở Dữ Liệu (gv2023600455)
('2023600455', 'CL01'),
('2023600456', 'CL01'),
('2023600457', 'CL01'),
('2023600458', 'CL01'),
('2023600459', 'CL01'),

-- Lớp CL02: Toán Cao Cấp (gv2023600456)
('2023600455', 'CL02'),
('2023600457', 'CL02'),
('2023600460', 'CL02'),
('2023600461', 'CL02'),

-- Lớp CL03: Trí Tuệ Nhân Tạo (gv2023600455)
('2023600456', 'CL03'),
('2023600457', 'CL03'),
('2023600458', 'CL03'),
('2023600462', 'CL03'),

-- Lớp CL04: Mạng máy tính (gv2023600457)
('2023600455', 'CL04'),
('2023600458', 'CL04'),
('2023600459', 'CL04'),
('2023600460', 'CL04'),

-- Lớp CL05: Phát triển phần mềm (gv2023600458)
('2023600456', 'CL05'),
('2023600457', 'CL05'),
('2023600459', 'CL05'),
('2023600461', 'CL05'),
('2023600462', 'CL05'),

-- Lớp CL06: Vi điều khiển và IoT (gv2023600459)
('2023600455', 'CL06'),
('2023600458', 'CL06'),
('2023600460', 'CL06'),
('2023600462', 'CL06'),

-- Lớp CL07: Phân tích dữ liệu (gv2023600455)
('2023600456', 'CL07'),
('2023600457', 'CL07'),
('2023600460', 'CL07'),
('2023600461', 'CL07');

