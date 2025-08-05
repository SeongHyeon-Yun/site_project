// 드롭다운 메뉴 클릭 시 버튼 이름 변경
document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function () {
        document.querySelector('.dropdown-toggle').textContent = this.textContent;
    });
});

price_input.addEventListener('input', function () {
    // 숫자만 남기기
    let value = this.value.replace(/[^0-9]/g, '');

    // 천단위 콤마 찍기
    this.value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
});
