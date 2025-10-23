/* 
================================================================
========== API XEM THÔNG TIN SINH VIÊN THEO MÃ MÔN HỌC =========
================================================================
*/
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-course-form");
  if (!form) {
    console.error("Không tìm thấy form #search-course-form. (Kiểm tra template)");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Lấy input
    const input = document.getElementById("courseIdInput");
    if (!input) {
      alert("Thiếu input với id='courseIdInput'! Kiểm tra lại HTML.");
      return;
    }
    const courseId = input.value.trim();
    if (!courseId) return alert("Vui lòng nhập mã môn học!");

    // Gửi request
    let res;
    try {
      res = await fetch(`/api/admin_course_detail/${encodeURIComponent(courseId)}/`);
    } catch (err) {
      console.error("Fetch error:", err);
      alert("Lỗi kết nối tới server.");
      return;
    }

  let data;
  try {
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Lỗi ${res.status}: ${text}`);
    }
    data = await res.json();
  } catch (err) {
    console.error("Lỗi khi đọc dữ liệu:", err);
    alert("Server trả về dữ liệu không hợp lệ hoặc lỗi kết nối.");
    return;
  }


    // Lấy vùng hiển thị
    let infoDiv = document.querySelector(".student-course-content");
    console.log("infoDiv (selector .teacher-infor-content):", infoDiv);
    // Nếu infoDiv không tồn tại, tạo vào sau phần .student-infor-title (nếu có)
    if (!infoDiv) {
      const parent = document.querySelector(".student-infor.teacher-infor") || document.body;
      infoDiv = document.createElement("div");
      infoDiv.className = "teacher-infor-content";
      parent.appendChild(infoDiv);
      console.warn(".teacher-infor-content không tồn tại — mình đã tự tạo phần tử này tạm thời.");
    }

    // Đảm bảo các phần con tồn tại (tạo nếu cần)
    const ensureChild = (cls, defaultText = "") => {
      let el = infoDiv.querySelector("." + cls);
      if (!el) {
        el = document.createElement("div");
        el.className = cls;
        el.textContent = defaultText;
        infoDiv.appendChild(el);
        console.warn(`Tạo phần tử .${cls} vì không tìm thấy trong DOM.`);
      }
      return el;
    };

    const cidEl = ensureChild("courseId-classId", "Mã môn: - Mã lớp:");
    const tnameEl = ensureChild("teacher-name", "Tên giảng viên:");
    const listDiv = ensureChild("list-student", "");

    // Kiểm tra lỗi từ API
    if (data && data.error) {
      cidEl.innerText = "";
      tnameEl.innerText = "";
      listDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
      return;
    }

    // Bảo đảm data.students là mảng
    const students = Array.isArray(data.students) ? data.students : [];

    // Cập nhật nội dung
    try {
      cidEl.innerText = `Mã môn: ${data.courseId ?? ""} - Mã lớp: ${data.classId ?? ""}`;
      tnameEl.innerText = `Tên giảng viên: ${data.teacherName ?? ""}`;
    } catch (err) {
      console.error("Lỗi khi cập nhật text:", err);
    }

    // Render bảng sinh viên
    if (students.length === 0) {
      listDiv.innerHTML = "<p>Không có sinh viên hoặc dữ liệu sinh viên rỗng.</p>";
    } else {
      let html = `
        <table border="1" cellspacing="0" cellpadding="5">
          <thead>
            <tr>
              <th>Mã sinh viên</th>
              <th>Tên sinh viên</th>
              <th>Chuyên ngành</th>
              <th>Lớp</th>
            </tr>
          </thead>
          <tbody>
      `;
      students.forEach(st => {
        html += `
          <tr>
            <td>${st.studentId ?? ""}</td>
            <td>${st.fullName ?? ""}</td>
            <td>${st.major ?? ""}</td>
            <td>${st.className ?? ""}</td>
          </tr>
        `;
      });
      html += `</tbody></table>`;
      listDiv.innerHTML = html;
    }

    console.log("Hiển thị xong. students.length =", students.length);
  });
});
/* 
================================================================
============ API XEM THÔNG TIN GIẢNG VIÊN THEO KHOA ============
================================================================
*/
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("search-department-form");
  if (!form) {
    console.error("Không tìm thấy form #search-department-form.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // --- Lấy giá trị nhập ---
    const input = document.getElementById("department-input");
    if (!input) {
      alert("Thiếu input với id='department-input'!");
      return;
    }

    const department = input.value.trim();
    if (!department) {
      alert("Vui lòng nhập tên khoa!");
      return;
    }

    // --- Gửi request đến API ---
    let res, data;
    try {
      res = await fetch(`/api/department_teacher/${encodeURIComponent(department)}/`);
      data = await res.json();
    } catch (err) {
      console.error("Lỗi fetch hoặc JSON:", err);
      alert("Không thể kết nối tới server.");
      return;
    }

    // --- Chọn vùng hiển thị ---
    const infoDiv = document.querySelector(".teacher-course-content");
    if (!infoDiv) {
      console.error("Không tìm thấy .teacher-course-content trong DOM.");
      return;
    }

    // --- Kiểm tra lỗi từ API ---
    if (data.error) {
      infoDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
      return;
    }

    // --- Hiển thị bảng dữ liệu ---
    const teachers = data.teachers || [];
    if (teachers.length === 0) {
      infoDiv.innerHTML = `<p>Không có giảng viên nào trong khoa "${data.department}".</p>`;
      return;
    }

    let html = `
      <h4>Khoa: ${data.department}</h4>
      <table border="1" cellspacing="0" cellpadding="6" style="margin-top:10px; border-collapse:collapse; width:100%;">
        <thead>
          <tr style="background-color:#f2f2f2;">
            <th>Mã giảng viên</th>
            <th>Họ tên</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
    `;

    teachers.forEach(t => {
      html += `
        <tr>
          <td>${t.teacherId ?? ""}</td>
          <td>${t.fullName ?? ""}</td>
          <td>${t.email ?? ""}</td>
        </tr>
      `;
    });

    html += `</tbody></table>`;
    infoDiv.innerHTML = html;

    console.log("Hiển thị danh sách giảng viên xong. Số lượng:", teachers.length);
  });
});
/* 
============================================================================
============ API GỬI THÔNG BÁO SỰ KIỆN CHO SINH VIÊN VÀ GIẢNG VIÊN =========
============================================================================
*/
document.getElementById("event-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const title = document.getElementById("event-title").value.trim();
  const time = document.getElementById("event-time").value;
  const receiver = document.getElementById("event-receiver").value;

  if (!title || !time) {
    alert("Vui lòng nhập đủ thông tin.");
    return;
  }

  try {
    const res = await fetch("/api/admin_event/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
      },
      body: JSON.stringify({ title, time, receiver }),
    });

    const text = await res.text();
    console.log("Response text:", text);

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      console.error("Không phải JSON:", text);
      data = {};
    }

    if (res.ok) {
      alert("✅ " + (data.message || "Gửi thông báo thành công!"));
      e.target.reset();
    } else {
      alert("❌ " + (data.error || "Lỗi không xác định"));
    }
  } catch (err) {
    alert("❌ Không thể gửi thông báo.");
    console.error(err);
  }
});