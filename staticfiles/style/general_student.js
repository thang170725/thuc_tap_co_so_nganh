document.addEventListener("DOMContentLoaded", () => {
    const bell = document.getElementById("bell-icon");
    const infoBox = document.getElementById("announcement-container");

    let isVisible = false;

    // Hover vào chuông => hiện box
    bell.addEventListener("mouseenter", () => {
        infoBox.classList.add("show");
    });

    // Rời chuông + box => ẩn box
    document.addEventListener("mouseover", (e) => {
        if (!bell.contains(e.target) && !infoBox.contains(e.target)) {
            infoBox.classList.remove("show");
            isVisible = false;
        }
    });

    // Click chuông => toggle hiển thị/ẩn
    bell.addEventListener("click", () => {
        isVisible = !isVisible;
        if (isVisible) {
            infoBox.classList.add("show");
        } else {
            infoBox.classList.remove("show");
        }
    });
});
