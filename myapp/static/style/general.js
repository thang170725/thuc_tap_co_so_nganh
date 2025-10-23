/* 
====================================================================================
============ API SINH VIÊN VÀ GIẢNG VIÊN XEM THÔNG BÁO SỰ KIỆN TỪ ADMIN ============
====================================================================================
*/
const userRole = "{{ user_role }}"; // Django sẽ thay đúng vai trò
  fetch(`/api/events/?role=${userRole}`)
    .then(res => res.json())
    .then(data => {
      const container = document.querySelector(".upcoming-events");
      container.innerHTML = "<h3>Sự kiện sắp tới</h3>";
      data.events.forEach(ev => {
        container.innerHTML += `
          <div class="event-card">
            <i class="fas fa-calendar-alt"></i>
            <div class="event-details">
              <p>${ev.title}</p>
              <small>${new Date(ev.time).toLocaleString()}</small>
            </div>
          </div>
        `;
      });
    })
    .catch(err => console.error("Lỗi khi tải sự kiện:", err));