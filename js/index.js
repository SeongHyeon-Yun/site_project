const sign_btn = document.getElementById('sign_btn');
if (sign_btn) {
    sign_btn.addEventListener('click', () => {
        window.location = "sign_up.html";
    });
}

// 한글 입력 막을 input들의 id 모음
const blockKoreanIds = ['user_id'];

blockKoreanIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('input', () => {
            el.value = el.value.replace(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/g, '');
        });
    }
});

// 숫자만 입력 가능하게 하는 함수
function onlyNumberInput(selector) {
    const el = document.getElementById(selector);
    if (!el) return;

    el.addEventListener('input', () => {
        el.value = el.value.replace(/[^0-9]/g, '');
    });
}

const casinoBtn = document.getElementById('casino');
const slotBtn = document.getElementById('slot');
const casinoSection = document.querySelector('.casino-section');
const slotSection = document.querySelector('.slot-section');

function toggleGame() {
    if (casinoBtn.checked) {
        casinoSection.style.display = "block";
        slotSection.style.display = "none";
    } else {
        casinoSection.style.display = "none";
        slotSection.style.display = "block";
    }
}

// 초기 상태 적용
toggleGame();

// 라디오 클릭 시 변경
casinoBtn.addEventListener('click', toggleGame);
slotBtn.addEventListener('click', toggleGame);


// 숫자만 허용할 input들
onlyNumberInput('bank_num');     // 계좌번호
onlyNumberInput('user_phone');   // 전화번호