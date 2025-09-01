const monthEl = document.getElementById("month");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

let month = parseInt(monthEl.dataset.month);

prevBtn.addEventListener("click", () => {
    month = month - 1;
    if (month < 1) month = 12;  // 1월 → 이전 = 12월

    // 이동
    window.location.href = `/notes/check_day?month=${month}`;
});

nextBtn.addEventListener("click", () => {
    month = month + 1;
    if (month > 12) month = 1;  // 12월 → 다음 = 1월

    // 이동
    window.location.href = `/notes/check_day?month=${month}`;
});