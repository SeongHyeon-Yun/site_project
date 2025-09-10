const menuBtn = document.getElementById('menu-btn');
const userBtn = document.getElementById('user-btn');
const leftBox = document.getElementById('left_box');
const rightBox = document.getElementById('right_box');

menuBtn.addEventListener('click', function () {
    leftBox.classList.toggle("active");   // 왼쪽 토글
    rightBox.classList.remove("active");  // 오른쪽 토글

});

userBtn.addEventListener('click', function () {
    rightBox.classList.toggle("active");  // 오른쪽 토글
    leftBox.classList.remove("active");   // 왼쪽 토글
});


const sport_con = document.querySelectorAll('.sport-con');
sport_con.forEach(btn => {
    btn.addEventListener('click', function () {
        const sport_location = btn.querySelector('.sport_location').innerText;

        switch (sport_location.trim()) {
            case '축구':
                window.location.href = '/games/sport/?type=1';
                break;
            case '야구':
                window.location.href = '/games/sport/?type=9';
                break;
            case '농구':
                window.location.href = '/games/sport/?type=3';
                break;
            case '배구':
                window.location.href = '/games/sport/?type=5';
                break;
            case '하키':
                window.location.href = '/games/sport/?type=4';
                break;
            case '미식축구':
                window.location.href = '/games/sport/?type=7';
                break;
            case 'E-SPORT':
                window.location.href = '/games/sport/?type=10';
                break;
        }
    });
});