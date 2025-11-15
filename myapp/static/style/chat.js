document.addEventListener("DOMContentLoaded", () => {
    const icon = document.getElementById("ai-chat-icon");
    const popup = document.getElementById("ai-chat-popup");
    const closeBtn = document.getElementById("ai-chat-close");
    const form = document.getElementById("ai-chat-form");
    const input = document.getElementById("ai-chat-input");
    const body = document.getElementById("ai-chat-body");

    icon.addEventListener("click", () => popup.style.display = "flex");
    closeBtn.addEventListener("click", () => popup.style.display = "none");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;

        body.innerHTML += `<p><strong>Bạn:</strong> ${question}</p>`;
        input.value = "";

        try {
            const res = await fetch(`/api/chat_ai/?q=${encodeURIComponent(question)}`);
            const data = await res.json();
            body.innerHTML += `<p><strong>AI:</strong> ${data.answer || "Có lỗi xảy ra"}</p>`;
            body.scrollTop = body.scrollHeight;
        } catch (err) {
            body.innerHTML += `<p><strong>AI:</strong> Lỗi mạng</p>`;
        }
    });
});
