let selectedGames = [];
const pick = document.querySelectorAll('.pick');

// ✅ 항상 "sport" 이라는 key로 관리
const STORAGE_KEY = "sport";

// ============================
// 📌 로컬스토리지 핸들러
// ============================
function getSelectedGames() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
}

function saveSelectedGames(games) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(games));
}

// ============================
// 📌 베팅 내역 그려주기
// ============================
function renderBettingList() {
    let bettingListEl = document.getElementById("selected_games");
    let selected = getSelectedGames();

    // 초기화
    bettingListEl.innerHTML = "";

    if (selected.length === 0) {
        bettingListEl.innerHTML = "<p>선택된 베팅이 없습니다.</p>";
        updateCartOdds(1); // 아무것도 없으면 기본 1.00
        return;
    }

    selected.forEach(game => {
        let item = document.createElement("div");
        item.className = "special_game";
        item.innerHTML = `
            <input type="hidden" data-marketId="${game.marketId}" name="market_id" value="${game.marketId}">
            <input type="hidden" data-eventId="${game.eventId}" name="event_id" value="${game.eventId}">
            <input type="hidden" data-sportId="${game.sportType}" name="sport_id" value="${game.sportType}">
            <span data-pick="${game.pick}" class="pick">${game.pick}</span>
            <span data-teamname="${game.teamName}" class="ateam">${game.teamName}</span>
            <span data-odds="${game.odds}" class="odds">${game.odds}</span>
            <span data-point="${game.point || "-"}" class="point">${game.point || "-"}</span>
            <span data-smarket="(${game.pick})" class="smarket">(${game.pick})</span>
        `;
        bettingListEl.appendChild(item);
    });

    // ✅ 리스트를 그린 후 바로 배당 합산 업데이트
    updateCartOddsFromDOM();
}

// ============================
// 📌 UI에 pick_active 복원
// ============================
function restorePickActive() {
    let selected = getSelectedGames();

    selected.forEach(game => {
        let target = document.querySelector(
            `.pick[data-market-id="${game.marketId}"][data-pick="${game.pick}"][data-odds="${game.odds}"][data-teamname="${game.teamName}"]`
        );
        if (target) {
            target.classList.add("pick_active");
        }
    });
}

// ============================
// 📌 선택 클릭 이벤트
// ============================
pick.forEach(element => {
    element.addEventListener('click', () => {
        let select_pick = element.dataset.pick;
        let select_teamName = element.dataset.teamname;
        let select_odds = element.dataset.odds;
        let select_point = element.dataset.point;
        let select_marketId = element.dataset.marketId;
        let select_eventId = element.dataset.eventId;
        let select_sportType = element.dataset.sportType;

        // 로컬스토리지 가져오기
        let selected = getSelectedGames();

        // 이미 활성화된 경우 → 해제
        if (element.classList.contains("pick_active")) {
            element.classList.toggle("pick_active");
            selected = selected.filter(game => game.marketId !== select_marketId);

            console.log("해제:", select_marketId);
        } else {
            // 같은 marketId 그룹 전부 해제
            document.querySelectorAll(`.pick[data-market-id="${select_marketId}"]`)
                .forEach(p => p.classList.remove('pick_active'));

            // 현재 클릭한 것 활성화
            element.classList.toggle("pick_active");

            // 기존 같은 marketId 값 제거 후 새 값 추가
            selected = selected.filter(game => game.marketId !== select_marketId);
            selected.push({
                pick: select_pick,
                teamName: select_teamName,
                odds: select_odds,
                point: select_point,
                marketId: select_marketId,
                eventId: select_eventId,
                sportType: select_sportType
            });

        }

        saveSelectedGames(selected);
        renderBettingList(); // ✅ renderBettingList 안에서 cart_odds 갱신됨
        // console.log("📌 현재 selected_games:", selected);
    });
});

// ============================
// 🟢 페이지 로드 이벤트
// ============================
window.addEventListener("DOMContentLoaded", () => {
    // ✅ 새로고침이면 저장소 초기화
    if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
        localStorage.removeItem(STORAGE_KEY);
        console.log("새로고침 감지 → 초기화");
    }

    renderBettingList();
    restorePickActive();
});

// ============================
// 🟢 배당 합산 함수
// ============================
function updateCartOddsFromDOM() {
    const items = document.querySelectorAll('.special_game');
    let result_odds = 1;

    items.forEach(item => {
        let floatOdds = parseFloat(item.querySelector('.odds').innerText);
        if (!isNaN(floatOdds)) {
            result_odds *= floatOdds;
        }
    });

    updateCartOdds(result_odds);
}

function updateCartOdds(value) {
    const cart_odds = document.getElementById('cart_odds');
    if (cart_odds) {
        cart_odds.innerText = value.toFixed(2);
    }
}
