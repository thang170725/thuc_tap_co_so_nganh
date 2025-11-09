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

function loadWeather(containerId, city="Hà Nội") {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = "Đang tải thời tiết...";

    fetch(`/api/weather/?city=${encodeURIComponent(city)}`)
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            container.innerHTML = `<span style="color:red;">${data.error}</span>`;
            return;
        }

        const iconUrl = `http://openweathermap.org/img/wn/${data.icon}@2x.png`;

        container.innerHTML = `
            <div class="weather-widget">
                <h4>Thời tiết ${data.city}</h4>
                <div class="weather-info">
                    <img src="${iconUrl}" alt="icon thời tiết" class="weather-icon">
                    <div class="weather-details">
                        <p><strong>${data.temp}°C</strong></p>
                        <p>${data.desc}</p>
                        <p>Độ ẩm: ${data.humidity}%</p>
                    </div>
                </div>
            </div>
        `;
    })
    .catch(err => {
        console.error(err);
        container.innerHTML = `<span style="color:red;">Không thể tải dữ liệu</span>`;
    });
}

// Auto load khi DOM sẵn sàng
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("weather-container")) {
        loadWeather("weather-container");
    }
});