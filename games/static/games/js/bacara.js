const moneyChangeBtn = document.getElementById("moneyChangeBtn");


moneyChangeBtn.addEventListener("click", function () {
    const userMoney = moneyChangeBtn.dataset.userMoney;
    const userName = moneyChangeBtn.dataset.userName;
    const inputMoney = document.getElementById("input_money").value;
    const moneyType = document.querySelector("#moneySelect").value;
    const get_money = document.getElementById("get_money").value;

    console.log(userMoney);
    console.log(userName);
    console.log(inputMoney);
    console.log(moneyType);
    console.log(get_money)


    if (isNaN(inputMoney) || inputMoney <= 0) {
        alert("올바른 금액을 입력해주세요.");
        window.location.reload();
        return;
    }

    if (moneyType == "in") {
        if (parseInt(inputMoney) > parseInt(userMoney)) {
            alert("보유한 금액보다 큰 금액은 전환할 수 없습니다.");
            window.location.reload();
            return;
        }
    }


    if (moneyType == "out") {
        if (parseInt(inputMoney) > parseInt(get_money)) {
            alert("게임 머니보다 큰 금액은 출금할 수 없습니다.");
            window.location.reload();
            return;
        }
    }

    const data = {
        money: inputMoney,
        username: userName,
        money_type: moneyType
    };


    // ✅ fetch 로 POST 요청
    fetch("/games/money_change/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")  // CSRF 토큰 필요
        },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(result => {
            alert(result.message);
            window.location.reload();
        })
        .catch(err => console.error("❌ 에러:", err));
});

// ✅ CSRF 토큰 가져오기 함수 (Django 공식 문서 방식)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}