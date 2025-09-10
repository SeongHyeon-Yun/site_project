const dp_btns = document.querySelectorAll('.dp-btn');
const priceInput = document.getElementById('id_price');
const bonus_option = document.querySelector('select[name="bonus"]');

// 금액 버튼 클릭 이벤트
dp_btns.forEach((btn) => {
    btn.addEventListener('click', () => {
        const price = btn.innerText.trim();
        switch (price) {
            case '1만원': priceInput.value = 10000; break;
            case '3만원': priceInput.value = 30000; break;
            case '5만원': priceInput.value = 50000; break;
            case '10만원': priceInput.value = 100000; break;
            case '30만원': priceInput.value = 300000; break;
            case '50만원': priceInput.value = 500000; break;
            case '100만원': priceInput.value = 1000000; break;
            case '150만원': priceInput.value = 1500000; break;
            case '200만원': priceInput.value = 2000000; break;
            case "정정하기": priceInput.value = ""; break;
        }
    });
});
// 입금/출금 버튼 클릭 이벤트
const money_btn = document.getElementById('money-btn');
money_btn.addEventListener('click', () => {
    const result_price = priceInput.value;
    const username = money_btn.dataset.username;
    const type = money_btn.dataset.type;

    let pass = null;
    let result_bonus = null;
    let data = {};   // ✅ 미리 선언

    if (type === 'deposit') {
        result_bonus = bonus_option.value;

        data = {
            price: result_price,
            username: username,
            bonus: result_bonus,
            type: type
        };

    } else {
        const pass_check = document.getElementById('pass').value;
        pass = money_btn.dataset.pass;

        if (pass_check !== pass) {
            alert("비밀번호가 일치하지 않습니다.");
            return;
        } else {
            data = {
                price: result_price,
                username: username,
                type: type
            };
        }
    }

    // ✅ 여기서 title 정의
    const title = (type === "withdraw") ? "출금" : "입금";

    fetch("/amount/deposit/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("서버 응답:", data);  // ✅ 서버에서 받은 데이터 확인
            if (data.status === "success") {
                alert(`${title} 신청이 완료되었습니다.`);
            } else {
                alert(`${title} 신청에 실패했습니다. 사유: ${data.message || "알 수 없음"}`);
            }
            window.location.href = "/amount/deposit/";
        })
        .catch((err) => {
            console.error("에러 발생:", err);
            alert("서버 오류가 발생했습니다.");
        });
});


// 👉 CSRF 토큰 가져오기 함수
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
