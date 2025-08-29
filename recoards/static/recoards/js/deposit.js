const price_input = document.getElementById('price_input');
const price_btns = document.querySelectorAll('.price_btn');

let value = 0;

// 버튼 클릭 이벤트
price_btns.forEach((btn) => {
    btn.addEventListener('click', () => {
        const money = parseInt(btn.dataset.amount, 10);
        if (money === 0) {
            // 정정하기 → 초기화
            value = 0;
            price_input.value = '';
            console.log('정정하기 클릭 → 초기화됨');
        } else {
            // 금액 추가
            value += money;
            price_input.value = value.toLocaleString();
        }
    });
});

// 수기 입력 이벤트
price_input.addEventListener('input', (e) => {
    // 숫자만 추출
    let raw = e.target.value.replace(/[^0-9]/g, '');

    if (raw === '') {
        value = 0;
        e.target.value = '';
        return;
    }

    // 숫자로 변환
    value = parseInt(raw, 10);

    // 콤마 붙여서 다시 표시
    e.target.value = value.toLocaleString();
});

const bank_answer = document.getElementById('bank_answer');

if (bank_answer) {
    bank_answer.addEventListener('click', function () {
        confirm("입금 계좌를 확인하시겠습니까?");
    })
}

const deposit_btn = document.getElementById('deposit_btn');
deposit_btn.addEventListener('click', function () {
    const text = deposit_btn.textContent.trim(); // 공백 제거
    if (text === "입금 하기") {
        if (confirm("입금을 진행하시겠습니까?")) {
            deposit_form.submit(); // Django 뷰로 POST 전송
        }
    } else if (text === "출금 하기") {
        if (confirm("출금을 진행하시겠습니까?")) {
            deposit_form.submit();
        }
    }
});