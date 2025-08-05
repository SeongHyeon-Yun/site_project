const casino_imgs = document.getElementById('casino_imgs');
const slot_imgs = document.getElementById('slot_imgs');

function getSelectedGameType() {
    return document.querySelector('input[name="gameType"]:checked')?.id;
}

function toggleGameImages() {
    const select_game = getSelectedGameType();
    if (select_game === "casino") {
        casino_imgs.classList.remove('hidden');
        slot_imgs.classList.add('hidden');
    } else {
        casino_imgs.classList.add('hidden');
        slot_imgs.classList.remove('hidden');
    }
}

// 1️⃣ 초기 상태 설정
toggleGameImages();

// 2️⃣ 라디오 변경 시 상태 갱신
document.querySelectorAll('input[name="gameType"]').forEach(radio => {
    radio.addEventListener('change', toggleGameImages);
});
