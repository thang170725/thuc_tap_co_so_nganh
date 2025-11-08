document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/teacher/statistics/")
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Gán dữ liệu thống kê
            document.getElementById("total_classes").textContent = data.total_classes;
            document.getElementById("total_hours").textContent = data.total_hours.toFixed(1);
            document.getElementById("total_courses").textContent = data.total_courses;

            // Biểu đồ cột
            const labels = Object.keys(data.per_day);
            const values = Object.values(data.per_day);

            const ctx = document.getElementById("dayChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Số buổi dạy theo ngày",
                        data: values,
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(err => {
            console.error("Lỗi:", err);
            alert("Không thể tải thống kê lịch dạy.");
        });
});
