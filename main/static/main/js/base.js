const service = document.getElementById('service');
const use_menual = document.getElementById('use-menual');

service.addEventListener('click', function () {
    const service_menu = document.getElementById('service_menu');
    const use_menu = document.getElementById('use_menu');

    // service_menu 토글
    service_menu.classList.toggle('hidden');

    // 다른 메뉴는 무조건 닫기
    use_menu.classList.add('hidden');
});

use_menual.addEventListener('click', function () {
    const service_menu = document.getElementById('service_menu');
    const use_menu = document.getElementById('use_menu');

    // use_menu 토글
    use_menu.classList.toggle('hidden');

    // 다른 메뉴는 무조건 닫기
    service_menu.classList.add('hidden');
});
