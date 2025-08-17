
// 머니 선택 창
const casino_btn = document.querySelectorAll('.money-top-menu');
casino_btn.forEach(btn => {
    btn.addEventListener('click', () => {
        // 모든 버튼에서 active 제거
        casino_btn.forEach(b => b.classList.remove('active'));
        // 클릭한 버튼만 active 추가
        btn.classList.add('active');
    });
});


// 머니 전환 금액 입력
const moneyinput = document.getElementById('moneyinput');
let value = 0
moneyinput.addEventListener('input', function () {
    // 1) 한글 제거
    value = this.value.replace(/[ㄱ-ㅎㅏ-ㅣ가-힣]/g, '');

    // 2) 숫자만 남기기 (영어/기호 다 제거)
    value = value.replace(/[^0-9]/g, '');

    // 3) 숫자를 정수로 바꾸고 콤마 붙이기
    if (value) {
        this.value = parseInt(value, 10).toLocaleString('ko-KR');
    } else {
        this.value = '';
    }
});

// 현재 머니값 가져오기
const currenMoney = document.getElementById('currenMoney');
let onlyNumber = parseInt(currenMoney.textContent.replace(/[^0-9]/g, ''), 10) || 0;

// 머니 버튼 기능
const moneyBtn = document.querySelectorAll('.moneyBtn');
moneyBtn.forEach(btn => {
    btn.addEventListener('click', function () {
        let current = parseInt(value || '0', 10); // value를 정수로 변환
        
        switch (btn.textContent.trim()) {
            case '5천원':
                current += 5000;
                break;
            case '1만원':
                current += 10000;
                break;
            case '3만원':
                current += 30000;
                break;
            case '5만원':
                current += 50000;
                break;
            case '10만원':
                current += 100000;
                break;
            case '50만원':
                current += 500000;
                break;
            case '100만원':
                current += 1000000;
                break;
            case '전액':
                current = onlyNumber;
                break;
        }
        value = current; // 다시 전역 변수에 숫자 저장
        moneyinput.value = current.toLocaleString('ko-KR'); // 입력창에도 반영
    });
});