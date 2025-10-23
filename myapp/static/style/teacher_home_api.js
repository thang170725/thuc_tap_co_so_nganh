document.getElementById("announcement-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const response = await fetch("/api/send_announcement/", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  document.getElementById("msg").innerText = data.message || data.error;
});
/*
==================================================================
====== GỌI API VÀ HIỂN THỊ THỜI KHÓA BIỂU CỦA GIẢNG VIÊN =========
==================================================================
*/
async function renderTimetable() {
    const res = await fetch('/api/timetable_teacher/');
    const data = await res.json();
    // lấy phần tử có id="timetable-container"
    const container = document.getElementById('timetable-container');
    let html = '';
    
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
                        <span class="course-code">${slot.courseId} - ${slot.courseName}</span>
                        <span class="room">${slot.room} - ${slot.capacity}</span>
                    </div>
                    <div class="class-time">${slot.start} - ${slot.end}</div>
                </div>`;
            });
    }
    container.innerHTML = html;
}
renderTimetable();