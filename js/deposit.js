const menu_items = document.querySelectorAll('.menu-item');

menu_items.forEach(btn => {
    btn.addEventListener('click', function () {
        const text = btn.textContent;
        location_page(text)
    })
});

function location_page(e) {
    switch (e) {
        case '충전':
            window.location = '/deposit.html';
    }
}

const price_input = document.getElementById('price_input');
const price_btn = document.querySelectorAll('.price_btn');

price_btn.forEach(btn => {
    btn.addEventListener('click', () => {
        // 현재 input 값을 숫자로 변환
        let currentValue = parseInt(price_input.value.replace(/,/g, '')) || 0;

        const price_text = btn.textContent;
        let add_price = 0;

        switch (price_text) {
            case '1만원':
                add_price = 10000;
                break;
            case '5만원':
                add_price = 50000;
                break;
            case '10만원':
                add_price = 100000;
                break;
            case '50만원':
                add_price = 500000;
                break;
            case '100만원':
                add_price = 1000000;
                break;
            case '200만원':
                add_price = 2000000;
                break;
        }

        // 기존 값에 추가
        let newValue = currentValue + add_price;

        // input에 천단위 표시
        price_input.value = newValue.toLocaleString();
        console.log(price_input.value);
    });
});

price_input.addEventListener('input', function () {
    // 숫자만 남기기
    let value = this.value.replace(/[^0-9]/g, '');

    // 천단위 콤마 찍기
    this.value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
});
