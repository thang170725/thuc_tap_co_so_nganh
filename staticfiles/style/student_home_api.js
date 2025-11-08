/*
==================================================================
============= GỌI API VÀ HIỂN THỊ THỜI KHÓA BIỂU ================= 
==================================================================
*/
async function renderTimetable() {
    try{
        const res = await fetch('/api/timetable/');
        const data = await res.json();
        // lấy phần tử có id="timetable-container"
        const container = document.getElementById('timetable-container');
        let html = '';
        // duyệt qua từng ngày và danh sách tiết học
        for (const [day, slots] of Object.entries(data)) {
            if (slots.length === 0) continue;
            html += `<h3 style="margin-bottom: 5px;">${day}</h3>`;
            slots.forEach(slot => {
                // danh sách các màu có sẵn
                const colors = ['purple', 'blue', 'green', 'yellow'];
                // Chọn ngẫu nhiên 1 màu
                const randomColor = colors[Math.floor(Math.random()*colors.length)];

                html += `
                    <div class="class-card ${randomColor}">
                        <div class="class-info">
                            <span class="course-code" data-course=${slot.courseId}>${slot.courseName}</span>
                            <span class="course-title">${slot.teacher}</span>
                            <span class="room">${slot.room}</span>
                        </div>
                        <div class="class-time">${slot.start} - ${slot.end}</div>
                    </div>`;
            });
        }
        // hiển thị html ra giao diện
        container.innerHTML = html;
        // sau khi render xong => gắn sự kiện click cho tất cả .course-code
        document.querySelectorAll('.course-code').forEach(el => {
            el.addEventListener('click', async () => {
                const courseId = el.getAttribute('data-course');
                await showCoursePopup(courseId);
            });
        });
    } catch (error){
        console.error("Lỗi khi tải thời khóa biểu: ", error);
        document.getElementById('timetable-container').innerHTML = 
            "<p style='color:red'>Không thể tải thời khóa biểu.</p>";
    }  
}
// Gọi hàm khi trang đã tải xong
document.addEventListener("DOMContentLoaded", renderTimetable);

/*
==================================================================
====== GỌI API VÀ HIỂN THỊ BẢNG NỔI CHI TIẾT MÔN HỌC ============= 
==================================================================
*/
async function showCoursePopup(courseId) {
    try {
        const res = await fetch(`/api/course-detail/${courseId}/`);
        const data = await res.json();
        console.log(data);
        if (data.error) {
            alert(data.error);
            return;
        }
        // HTML bảng thông tin
        const popupHtml = `
            <div id="popup-overlay">
                <div id="popup-content">
                    <button id="popup-close">×</button>
                    <h3>Thông tin môn học</h3>
                    <table>
                        <tr><td><b>Mã môn:</b></td><td>${data.courseId}</td></tr>
                        <tr><td><b>Tên môn:</b></td><td>${data.courseName}</td></tr>
                        <tr><td><b>Số tín chỉ:</b></td><td>${data.credits}</td></tr>
                        <tr><td><b>Mô tả:</b></td><td>${data.descriptions}</td></tr>
                    </table>
                </div>
            </div>
        `;
        // thêm popup vào body
        document.body.insertAdjacentHTML('beforeend', popupHtml);
        // sự kiện đóng popup
        document.getElementById('popup-close').onclick = () => {
            document.getElementById('popup-overlay').remove();
        };
    } catch (error) {
        console.error("Lỗi khi tải chi tiết môn học:", error);
    }
}
/*
==================================================================
====== GỌI API VÀ HIỂN THỊ BẢNG NỔI THÔNG TIN SINH VIÊN ==========
==================================================================
*/
document.addEventListener("DOMContentLoaded", () => {
    const el = document.getElementsByClassName("get-username")[0];
    if (!el) return; // nếu chưa có phần tử thì dừng

    el.addEventListener('click', async () => {
        const studentId = el.getAttribute('data-student');
        await showInforPopup(studentId);
    });
});

async function showInforPopup(studentId) {
    try {
        const res = await fetch(`/api/student-infor-detail/${studentId}/`);
        const data = await res.json();
        console.log(data);
        if (data.error) {
            alert(data.error);
            return;
        }
        // HTML bảng thông tin
        const popupHtml = `
            <div id="popup-overlay">
                <div id="popup-content">
                    <button id="popup-close">×</button>
                    <h3>Thông tin sinh viên</h3>
                    <table>
                        <tr><td><b>Mã sinh viên:</b></td><td>${data.studentId}</td></tr>
                        <tr><td><b>Tên sinh viên:</b></td><td>${data.fullName}</td></tr>
                        <tr><td><b>Chuyên ngành:</b></td><td>${data.major}</td></tr>
                        <tr><td><b>Lớp:</b></td><td>${data.className}</td></tr>
                    </table>
                </div>
            </div>
        `;
        // thêm popup vào body
        document.body.insertAdjacentHTML('beforeend', popupHtml);
        // sự kiện đóng popup
        document.getElementById('popup-close').onclick = () => {
            document.getElementById('popup-overlay').remove();
        };
    } catch (error) {
        console.error("Lỗi khi tải thông tin sinh viên:", error);
    }
}
// ====================== HIỂN THỊ THÔNG BÁO VÀ NHẮC HẸN ====================== 
async function loadAnnouncements() {
    const container = document.getElementById('announcement-container');

    try {
        // gọi 2 api song song
        const [annRes, remRes] = await Promise.all([
            fetch('/api/announcements/'),
            fetch('/api/reminders/')
        ]);

        const annData = annRes.ok ? await annRes.json() : { announcements: [] };
        const remData = remRes.ok ? await remRes.json() : { reminders: [] };

        const all = [...(remData.reminders || []), ...(annData.announcements || [])];

        if (all.length === 0) {
            container.innerHTML = `<div class="child-information">Không có thông báo mới</div>`;
            return;
        }

        // Sắp xếp lại theo thời gian (mới nhất trước)
        all.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

        // Duyệt danh sách thông báo và tạo HTML
        container.innerHTML = all.map(a => `
            <div class="child-information">
                <strong>${a.title}</strong><br>
                ${a.content}<br>
                <small>${a.senderName} - ${a.createdAt}</small>
            </div>
        `).join('');

    } catch (err) {
        console.error("Lỗi khi gọi API:", err);
        container.innerHTML = `<div class="child-information">Lỗi khi tải thông báo</div>`;
    }
    }

loadAnnouncements();