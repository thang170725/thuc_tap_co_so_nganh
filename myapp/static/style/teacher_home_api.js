/*
==================================================================
====== GỌI API VÀ GỬI THÔNG BÁO ==================================
==================================================================
*/
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("send-ann-btn");
    const modal = document.getElementById("announcement-modal");
    const closeBtn = modal.querySelector(".close");
    const form = document.getElementById("announcement-form");
    const msg = document.getElementById("msg");

    // mở modal
    btn.addEventListener("click", (e) => {
        e.preventDefault();
        modal.style.display = "block";
    });

    // đóng modal khi click x
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
        msg.innerText = "";
        form.reset();
    });

    // đóng modal khi click ngoài content
    window.addEventListener("click", (e) => {
        if (e.target == modal) {
            modal.style.display = "none";
            msg.innerText = "";
            form.reset();
        }
    });

    // submit API
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const response = await fetch("/api/send_announcement/", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        msg.innerText = data.message || data.error;
    });
});

// document.getElementById("announcement-form").addEventListener("submit", async (e) => {
//   e.preventDefault();

//   const formData = new FormData(e.target);
//   const response = await fetch("/api/send_announcement/", {
//     method: "POST",
//     body: formData,
//   });

//   const data = await response.json();
//   document.getElementById("msg").innerText = data.message || data.error;
// });
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

document.addEventListener("DOMContentLoaded", () => {
    const exportBtn = document.getElementById("export-btn");
    if (!exportBtn) return;

    exportBtn.addEventListener("click", () => {
        fetch("/api/export_timetable/")  // URL an toàn từ Django
        .then(response => {
            if (!response.ok) {
                alert("Không thể xuất thời khóa biểu!");
                return;
            }
            return response.blob();
        })
        .then(blob => {
            if (!blob) return;
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "timetable.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => console.error(err));
    });
});
