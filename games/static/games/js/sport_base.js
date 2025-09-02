// 모바일 카트 토글
const bet_open = document.getElementById('open');
bet_open.addEventListener('click', function () {
    const bet_close = document.getElementById('close');
    const label = bet_open.querySelector('span');

    if (bet_close.style.display === "block") {
        bet_close.style.display = "none";
        label.innerText = "카트 열기";
    } else {
        bet_close.style.display = "block";
        label.innerText = "카트 닫기";
    }
});

// ✅ 합계 배당 + 당첨금 다시 계산 (상한선 포함)
function updateCartOdds() {
    const oddsList = document.querySelectorAll('.odds');
    let product = 1;

    oddsList.forEach((el) => {
        const value = parseFloat(el.innerText.trim());
        if (!isNaN(value)) {
            product *= value;
        }
    });

    // 합계 배당 표시
    const cart_odds = document.getElementById('cart_odds');
    if (cart_odds) {
        cart_odds.innerText = product > 1 ? product.toFixed(2) : "0";
    }

    // ✅ 베팅 금액 가져오기
    const bet_price = document.getElementById('bet_price');
    let betMoney = parseInt(bet_price.value.replace(/,/g, "")) || 0;

    // ✅ 게임 수에 따른 한도 계산
    const game_count = oddsList.length;
    const limit = game_count === 1 ? 1000000 : 3000000;

    if (betMoney > limit) {
        alert(limit.toLocaleString() + "원 이상 베팅은 불가능합니다.");
        betMoney = limit;
    }

    // ✅ 예상 당첨금 계산
    let multiply = Math.trunc(product * betMoney);

    // ✅ 당첨금 한도 (천만원)
    const maxWin = 10000000;
    if (multiply > maxWin) {
        alert('당첨 한도는 ' + maxWin.toLocaleString() + '원 입니다.');
        betMoney = Math.floor(maxWin / product);
        multiply = Math.trunc(product * betMoney);
    }

    // input 값 다시 세팅 (콤마 포함)
    bet_price.value = betMoney ? betMoney.toLocaleString() : "";

    // 당첨금 출력
    const result_money = document.getElementById('result_money');
    if (result_money) {
        result_money.innerText = multiply ? multiply.toLocaleString() : "0";
    }

    return product;
}

// 베팅금액 인풋창 숫자만 입력 + 문자 입력 시 알림 + 베팅 한도 당첨 한도 알림
const bet_price = document.getElementById('bet_price');
bet_price.addEventListener('input', function () {
    // 콤마 제거 후 숫자만 추출
    let rawValue = this.value.replace(/,/g, "");
    let onlyNumber = rawValue.replace(/[^0-9]/g, "");

    // 문자 입력이 있었으면 알림
    if (rawValue !== onlyNumber) {
        alert("숫자만 입력하세요");
    }

    // 숫자값으로 변환
    let betMoney = Number(onlyNumber);

    // 배팅 경기 갯수
    const oddsList = document.querySelectorAll('.odds');
    let game_count = oddsList.length;

    // 한계치 설정
    let limit = game_count === 1 ? 1000000 : 3000000;

    // 1. 기본 베팅 한도 체크
    if (betMoney > limit) {
        alert(limit.toLocaleString() + "원 이상 베팅은 불가능합니다.");
        betMoney = limit;
    }

    // 2. 예상 당첨금 계산
    const product = updateCartOdds(); // 현재 배당 곱 구하기
    let multiply = Math.trunc(product * betMoney);

    // 3. 당첨금 한도 체크 (천만원)
    const maxWin = 10000000;
    if (multiply > maxWin) {
        alert('당첨 한도는 ' + maxWin.toLocaleString() + '원 입니다.');

        // 당첨금이 천만원을 넘지 않도록 베팅금액을 줄임
        betMoney = Math.floor(maxWin / product);
        multiply = Math.trunc(product * betMoney);
    }

    // input 값 다시 세팅 (콤마 포함)
    this.value = betMoney ? betMoney.toLocaleString() : "";

    // 예상 당첨금 출력
    const result_money = document.getElementById('result_money');
    result_money.innerText = multiply ? multiply.toLocaleString() : "0";
});

// 베팅 경기 선택 하기
const select_active = document.querySelectorAll(".select_active");
select_active.forEach(btn => {
    btn.addEventListener("click", function () {
        const between = btn.closest(".between");
        const gameTitle = between.querySelector(".game_title");

        // 팀 이름 찾기
        const homeTeam = gameTitle.querySelector(".teams.home")?.innerText.trim();
        const awayTeam = gameTitle.querySelector(".teams.away")?.innerText.trim();
        const isHome = btn.classList.contains("home");
        const isAway = btn.classList.contains("away");
        const isDraw = btn.classList.contains("draw");

        // 베팅 타입 및 배당 찾기
        const betType = btn.querySelector("span:first-child")?.innerText.trim();
        const odds = btn.querySelector("span:last-child")?.innerText.trim();

        // 선택된 팀 이름
        let teamName = "";
        if (isHome) teamName = homeTeam;
        else if (isAway) teamName = awayTeam;
        else if (isDraw) teamName = homeTeam;
        else teamName = betType;

        // 같은 열(.game_odd) 블록 찾기
        const gameBlock = btn.closest(".game_odd");
        if (!gameBlock) {
            console.warn("gameBlock을 찾을 수 없음", btn);
            return;
        }

        // ✅ 히든 input(.market_type)에서 마켓 이름 가져오기
        const marketInput = gameBlock.parentElement.querySelector(".market_type");
        const marketName = marketInput && marketInput.value ? marketInput.value : "기본마켓";

        // 고유 ID (경기 + 마켓)
        const betId = `${homeTeam}_${awayTeam}_${marketName}`;

        // 카트 컨테이너
        const container = document.getElementById("selected_games");

        // 이미 선택된 항목 확인
        const exist = container.querySelector(`[data-id="${betId}"]`);

        // ✅ 이미 활성화된 버튼이면 → 해제
        if (btn.classList.contains("active")) {
            btn.classList.remove("active");
            btn.style.backgroundColor = "";
            btn.style.borderRadius = "";
            if (exist) exist.remove();
            updateCartOdds();
            return;
        }

        // ✅ 같은 열 안의 버튼들 해제
        gameBlock.querySelectorAll(".select_active").forEach(el => {
            el.classList.remove("active");
            el.style.backgroundColor = "";
            el.style.borderRadius = "";
        });

        // 카트에서도 같은 마켓 항목 제거
        if (exist) exist.remove();

        // ✅ 새로운 선택 적용
        btn.classList.add("active");
        btn.style.backgroundColor = "#ffc800";
        btn.style.borderRadius = "8px";

        // ✅ 버튼에서 dataset 가져오기
        const eventId = btn.dataset.eventId;
        const marketId = btn.dataset.marketId;
        const pick = btn.dataset.pick;


        // 카트에 추가
        const div = document.createElement("div");
        div.classList.add("bet_list");
        div.setAttribute("data-id", betId);

        div.innerHTML = `
                <div class="bet_teams" 
                    data-event-id="${eventId}" 
                    data-market-id="${marketId}" 
                    data-pick="${pick}"
                    data-point="${btn.dataset.point || ''}">
                    <span class="white_over">${teamName}</span>
                    <span>${betType}</span>
                    <span class="odds">${odds}</span>
                </div>
            `;

        container.appendChild(div);
        updateCartOdds();
    });
});


// 베팅 하기
const submit_btn = document.getElementById('submit_btn');
submit_btn.addEventListener('click', function () {
    const cart_odds = document.getElementById('cart_odds');
    const result_money = document.getElementById('result_money');
    const clean_money = bet_price.value.replace(/,/g, ""); // "1,000" → "1000"
    const user_money = Number(submit_btn.dataset.money);

    // ✅ 기본 검증
    if (cart_odds.innerHTML.trim() === "0") {
        alert('베팅 내역이 없습니다.');
        return;
    }

    if (user_money < clean_money) {
        alert('보유머니가 부족합니다.');
        return;
    }

    if (clean_money < 10000) {
        alert('최소 베팅금액은 1만원 이상입니다.');
        return;
    }

    // ✅ 카트 데이터 수집
    const cart = [];
    document.querySelectorAll(".bet_teams").forEach(item => {
        cart.push({
            event_id: item.dataset.eventId,
            market_id: item.dataset.marketId,
            pick: item.dataset.pick,
            odds: item.querySelector(".odds")?.innerText.trim() || null,
            point: item.dataset.point || null,   // ✅ 바로 dataset에서 읽기
        });
    });

    console.log("최종 카트 데이터:", cart);


    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput ? csrfInput.value : "";
    
    fetch("/games/betting/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            amount: clean_money,
            cart: cart,
        }),
    })
        .then(res => {
            console.log("응답 상태:", res.status);
            return res.json();
        })
        .then(data => {
            console.log("응답 JSON:", data);
            if (data.success) {
                alert("베팅 성공!");
                location.reload();
            } else {
                alert("실패: " + data.message);
            }
        })
        .catch(err => {
            console.error("fetch 에러:", err);
            alert("베팅 중 오류 발생");
        });

});