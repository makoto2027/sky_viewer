document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const themeBtn = document.getElementById("toggle-theme");

    // 初期テーマ読み込み
    const saved = localStorage.getItem("theme");
    if (saved) {
        body.classList.add(saved);
    } else {
        body.classList.add("light");
    }

    // ボタンクリックでテーマ切り替え
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            if (body.classList.contains("light")) {
                body.classList.remove("light");
                body.classList.add("dark");
                localStorage.setItem("theme", "dark");
            } else {
                body.classList.remove("dark");
                body.classList.add("light");
                localStorage.setItem("theme", "light");
            }
        });
    }
});
