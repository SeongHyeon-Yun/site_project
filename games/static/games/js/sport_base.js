// ✅ 요소 참조
const bet_price = document.getElementById('bet_price');
const result_money = document.getElementById('result_money');
const cart_odds = document.getElementById('cart_odds');

// ============================
// 📌 베팅 금액 및 예상 당첨금 계산 함수
// ============================
function calculateBetResult() {
    // 1. 숫자만 남기고 천단위 콤마 다시 추가
    let rawValue = bet_price.value.replace(/,/g, "");
    let onlyNumber = rawValue.replace(/[^0-9]/g, "");

    if (rawValue !== onlyNumber) {
        alert("숫자만 입력하세요");
    }

    let betMoney = Number(onlyNumber) || 0;

    // 2. 현재 배당 곱 읽기
    const float_cart_odds = parseFloat(cart_odds.innerText) || 1;

    // 3. 예상 당첨금 계산
    let multiply = Math.trunc(float_cart_odds * betMoney);

    // 4. input 값 다시 세팅 (콤마 포함)
    bet_price.value = betMoney ? betMoney.toLocaleString() : "";

    // 5. 예상 당첨금 출력
    result_money.innerText = multiply ? multiply.toLocaleString() : "0";
}

// 👉 베팅금액 입력 시 계산
bet_price.addEventListener('input', calculateBetResult);

// 👉 cart_odds 값 변경 감지해서 자동 계산
const observer = new MutationObserver(() => {
    calculateBetResult();
});
observer.observe(cart_odds, { childList: true, characterData: true, subtree: true });

const submit_btn = document.getElementById('submit_btn');
submit_btn.addEventListener('click', function (event) {
    event.preventDefault();  // ✅ 버튼 클릭 시 form 기본 제출 막기

    const selected_games = document.getElementById('selected_games');
    const games = selected_games.querySelectorAll('.special_game');
    const game_list = [];

    // 유저 정보
    const user_money = parseInt(submit_btn.dataset.money);
    const user_id = submit_btn.dataset.username;
    const bet_money = parseInt(bet_price.value.replace(/,/g, ""), 10) || 0;
    const win_money = parseInt(result_money.innerText.replace(/,/g, ""), 10) || 0;

    games.forEach(btn => {
        const market_id = btn.querySelector('input[name="market_id"]').value;
        const event_id = btn.querySelector('input[name="event_id"]').value;
        const pick = btn.querySelector('.pick').innerText;
        const team = btn.querySelector('.ateam').innerText;
        const odds = btn.querySelector('.odds').innerText;
        const point = btn.querySelector('.point').innerText;
        const market = btn.querySelector('.smarket').innerText;

        game_list.push({
            market_id: market_id,
            event_id: event_id,
            pick: pick,
            team: team,
            odds: odds,
            point: point,
            market: market,
            user_id: user_id,
            bet_money: bet_money,
            win_money: win_money
        });
    });

    // 베팅 유효성 검사
    if (bet_money < 10000) {
        alert("베팅 금액을 10,000원 이상 입력하세요");
        return;
    }
    if (bet_money > user_money) {
        alert("보유 금액이 부족합니다");
        return;
    }
    if (bet_money > 3000000) {
        alert("베팅 금액은 3,000,000원 이하로 입력하세요");
        return;
    }
    if (games.length == 1 && bet_money > 1000000) {
        alert("단폴 베팅은 100만원 이하만 가능합니다.");
        return;
    }
    if (game_list.length === 0) {
        alert("베팅할 경기를 선택하세요");
        return;
    }
    if (win_money > 10000000) {
        alert("예상 당첨금은 10,000,000원 이하만 가능합니다.");
        return;
    }
    if (games.length == 1 && win_money > 3000000) {
        alert("단폴 베팅은 3,000,000원 이하만 가능합니다.");
        return;
    }

    console.log(game_list);

    // ✅ fetch 구문 수정
    fetch('/games/betting/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            game_list: game_list
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("베팅 중 오류가 발생했습니다. 다시 시도해주세요.");
        });
});


// ============================
// 📌 CSRF 토큰 설정
// ============================
// ✅ CSRF 토큰 가져오기 헬퍼 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
