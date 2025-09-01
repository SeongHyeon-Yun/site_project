// 모바일 카트 토글
const bet_open = document.getElementById('open');
bet_open.addEventListener('click', function () {
    const bet_close = document.getElementById('close');
    const label = bet_open.querySelector('span');

    if (bet_close.style.display === "block") {
        bet_close.style.display = "none";
        label.innerText = "카드 열기";
    } else {
        bet_close.style.display = "block";
        label.innerText = "카드 닫기";
    }
});


// 합계 배당 구하기
const oddsList = document.querySelectorAll('.odds');
let product = 1;
oddsList.forEach((el) => {
    const value = parseFloat(el.innerText.trim());

    if (!isNaN(value)) {
        product *= value; // 곱하기
    }
});
const cart_odds = document.getElementById('cart_odds');
cart_odds.innerText = product


// 베팅금액 인풋창 숫자만 입력 + 문자 입력 시 알림 + 베팅 한도 당첨 한도 알림
const bet_price = document.getElementById('bet_price');
let odds = 0;

bet_price.addEventListener('input', function () {
    // 콤마 제거 후 숫자만 추출
    let rawValue = this.value.replace(/,/g, "");
    let onlyNumber = rawValue.replace(/[^0-9]/g, "");

    // 문자 입력이 있었으면 알림
    if (rawValue !== onlyNumber) {
        alert("숫자만 입력하세요");
    }

    // 숫자값으로 변환
    odds = Number(onlyNumber);

    // 배팅 경수 갯수
    let game_count = oddsList.length;

    // 한계치 설정
    let limit = game_count === 1 ? 1000000 : 3000000;

    // 1. 기본 베팅 한도 체크
    if (odds > limit) {
        alert(limit.toLocaleString() + "원 이상 베팅은 불가능합니다.");
        odds = limit;
    }

    // 2. 예상 당첨금 계산
    let multiply = Math.trunc(product * odds);

    // 3. 당첨금 한도 체크 (천만원)
    const maxWin = 10000000;
    if (multiply > maxWin) {
        alert('당첨 한도는 ' + maxWin.toLocaleString() + '원 입니다.');

        // 당첨금이 천만원을 넘지 않도록 베팅금액을 줄임
        odds = Math.floor(maxWin / product);

        multiply = Math.trunc(product * odds); // 다시 계산
    }

    // input 값 다시 세팅 (콤마 포함)
    this.value = odds ? odds.toLocaleString() : "";

    // 예상 당첨금 출력
    const result_money = document.getElementById('result_money');
    result_money.innerText = multiply ? multiply.toLocaleString() : "0";
});