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

bet_price.addEventListener('input', calculateBetResult);

// ============================
// 📌 베팅 하기
// ============================
const submit_btn = document.getElementById('submit_btn');
submit_btn.addEventListener('click', function () {
    const oddsList = document.querySelectorAll('.special_game');
    let bettingData = [];
    const userMoney = Number(submit_btn.dataset.money) || 0;
    const username = submit_btn.dataset.username || "";

    console.log("🟢 베팅 시도 by", username);
    console.log("🟢 보유 금액:", userMoney.toLocaleString());

    // ✅ 최소 1경기 이상 선택
    if (oddsList.length < 1) {
        alert("최소 1경기 이상 선택하세요");
        return;
    }

    // ✅ 경기 데이터 수집
    oddsList.forEach(div => {
        bettingData.push({
            market_id: div.querySelector('[data-marketid]')?.dataset.marketid,
            event_id: div.querySelector('[data-eventid]')?.dataset.eventid,
            sport_id: div.querySelector('[data-sportid]')?.dataset.sportid,
            pick: div.querySelector('[data-pick]')?.dataset.pick,
            teamname: div.querySelector('[data-teamname]')?.dataset.teamname,
            odds: div.querySelector('[data-odds]')?.dataset.odds,
            point: div.querySelector('[data-point]')?.dataset.point,
            smarket: div.querySelector('[data-smarket]')?.dataset.smarket
        });
    });

    // ✅ 베팅 금액 확인
    let betMoney = Number(bet_price.value.replace(/,/g, "")) || 0;
    if (betMoney <= 0) {
        alert("베팅 금액을 입력하세요");
        return;
    }

    // ✅ 예상 당첨금 계산
    const float_cart_odds = parseFloat(cart_odds.innerText) || 1;
    let multiply = Math.trunc(float_cart_odds * betMoney);

    // ✅ 단폴 / 2폴 이상 구분
    let maxBet, maxWin;
    if (oddsList.length === 1) {
        maxBet = 1000000;   // 단폴 최대 베팅
        maxWin = 3000000;   // 단폴 최대 당첨
    } else {
        maxBet = 3000000;   // 2폴 이상 최대 베팅
        maxWin = 10000000;  // 2폴 이상 최대 당첨
    }

    // ✅ 베팅금액 검증
    if (betMoney > maxBet) {
        alert(`최대 베팅 금액은 ${maxBet.toLocaleString()}원 입니다.`);
        return;
    }

    // ✅ 보유 금액 검증
    if (betMoney > userMoney) {
        alert("보유 금액이 부족합니다.");
        return;
    }

    // ✅ 당첨금액 검증
    if (multiply > maxWin) {
        alert(`최대 당첨 금액은 ${maxWin.toLocaleString()}원 입니다.`);
        return;
    }

    // ✅ 최종 데이터
    const payload = {
        bet_money: betMoney,
        expected_win: multiply,
        games: bettingData
    };

    // ✅ Django 뷰로 POST 전송
    fetch("/games/submit/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") // CSRF 토큰 필요
        },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("베팅이 완료되었습니다!");
                sessionStorage.clear();
                window.location.reload();
                // console.log("✅ 저장된 베팅:", data);
            } else {
                alert("베팅 실패");
                sessionStorage.clear();
                window.location.reload();
                // console.error("❌ 서버 응답:", data);
            }
        })
        .catch(err => {
            console.error("베팅 전송 오류:", err);
            alert("서버 오류가 발생했습니다.");
        });
});


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