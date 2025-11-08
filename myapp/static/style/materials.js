// === Hàm tải danh sách tài liệu dạng thẻ (cho teacher_home hoặc khu vực materialList) ===
async function loadMaterials() {
    const response = await fetch('/api/get_materials/');
    const data = await response.json();

    const list = document.getElementById('materialList');
    if (!list) return; // tránh lỗi nếu không có vùng này

    list.innerHTML = '';

    if (data.materials && data.materials.length > 0) {
        data.materials.forEach(m => {
            list.innerHTML += `
                <div class="material-item">
                    <b>${m.title}</b> <br>
                    Môn: ${m.courseName} <br>
                    <a href="${m.filePath}" target="_blank">📄 Xem tài liệu</a> <br>
                    <small>Đăng ngày: ${m.createdAt}</small>
                </div>
            `;
        });
    } else {
        list.innerHTML = "<p>Chưa có học liệu nào.</p>";
    }
}


// === Hàm upload tài liệu ===
async function uploadMaterial() {
    const courseId = document.getElementById('courseId')?.value;
    const title = document.getElementById('title')?.value;
    const file = document.getElementById('fileInput')?.files[0];

    if (!courseId || !title || !file) {
        alert("Vui lòng nhập đủ thông tin!");
        return;
    }

    const formData = new FormData();
    formData.append('courseId', courseId);
    formData.append('title', title);
    formData.append('file', file);

    const response = await fetch('/api/upload_material/', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.message) {
        alert(result.message);
        loadMaterials();
        loadMaterialTable(); // Cập nhật bảng luôn nếu có
    } else {
        alert("Lỗi: " + result.error);
    }
}


// === Hàm hiển thị danh sách tài liệu dạng bảng (cho trang teacher_materials.html) ===
function loadMaterialTable() {
    fetch("/api/materials/")
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("materials-container");
            if (!container) return; // tránh lỗi nếu không có vùng này

            if (!data || data.length === 0) {
                container.innerHTML = "<p>Chưa có tài liệu nào.</p>";
                return;
            }

            let html = `
                <table>
                    <tr>
                        <th>Mã tài liệu</th>
                        <th>Môn học</th>
                        <th>Tiêu đề</th>
                        <th>Mô tả</th>
                        <th>Ngày tải lên</th>
                    </tr>
            `;

            data.forEach(item => {
                html += `
                    <tr>
                        <td>${item.materialId}</td>
                        <td>${item.courseId}</td>
                        <td>${item.title}</td>
                        <td>${item.description || ''}</td>
                        <td>${item.uploadDate}</td>
                    </tr>
                `;
            });

            html += "</table>";
            container.innerHTML = html;
        })
        .catch(error => {
            console.error("Lỗi khi tải tài liệu:", error);
        });
}

async function uploadMaterial() {
  const form = document.getElementById('material-form');
  const msg = document.getElementById('upload-msg');
  const tableBody = document.querySelector('#materials-table tbody');

  const formData = new FormData(form);

  try {
    const response = await fetch("/api/upload_material/", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.message) {
      msg.style.color = "green";
      msg.textContent = data.message;

      // ✅ Thêm file vừa tải lên vào bảng
      const newRow = document.createElement("tr");
      newRow.innerHTML = `
        <td>${data.data.courseId}</td>
        <td>${data.data.title}</td>
        <td><a href="${data.data.file}" target="_blank">Xem</a></td>
        <td>${data.data.upload_date}</td>
      `;
      tableBody.prepend(newRow); // thêm lên đầu bảng

      // Reset form
      form.reset();
    } else {
      msg.style.color = "red";
      msg.textContent = data.error || "Lỗi tải lên.";
    }
  } catch (err) {
    msg.style.color = "red";
    msg.textContent = "Lỗi kết nối server.";
    console.error(err);
  }
}


// === Khi trang tải xong ===
document.addEventListener("DOMContentLoaded", () => {
    loadMaterials();      // gọi cho teacher_home (nếu có)
    loadMaterialTable();  // gọi cho teacher_materials.html (nếu có)
});
