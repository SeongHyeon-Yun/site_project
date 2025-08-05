const sign_btn = document.getElementById('sign_btn');
if (sign_btn) {
    sign_btn.addEventListener('click', () => {
        window.location.href = "/accounts/signUp/";  // Django URL
    });
}