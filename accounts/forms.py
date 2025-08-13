from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

BANK_CHOICES = [
    ("KB국민은행", "KB국민은행"),
    ("신한은행", "신한은행"),
    ("우리은행", "우리은행"),
    ("하나은행", "하나은행"),
    ("NH농협은행", "NH농협은행"),
    ("IBK기업은행", "IBK기업은행"),
    ("SC제일은행", "SC제일은행"),
    ("BNK부산은행", "BNK부산은행"),
    ("BNK경남은행", "BNK경남은행"),
    ("DGB대구은행", "DGB대구은행"),
    ("광주은행", "광주은행"),
    ("전북은행", "전북은행"),
    ("제주은행", "제주은행"),
    ("카카오뱅크", "카카오뱅크"),
    ("케이뱅크", "케이뱅크"),
    ("토스뱅크", "토스뱅크"),
    ("우체국예금", "우체국예금"),
    ("새마을금고", "새마을금고"),
    ("신협", "신협"),
]


class SignUpForm(UserCreationForm):
    bank = forms.CharField(
        widget=forms.Select(choices=BANK_CHOICES, attrs={"class": "sign-input"})
    )

    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={"placeholder": "아이디를 입력하세요"}),
        error_messages={
            "unique": "해당 아이디는 이미 존재합니다.",
            "required": "아이디를 입력해주세요.",
        },
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력하세요"})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력하세요"})
    )

    nickname = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "닉네임을 입력하세요"})
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "휴대폰번호를 입력하세요"})
    )

    account_holder = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "예금주를 입력하세요"})
    )

    account_number = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "계좌번호를 입력하세요"})
    )

    recommender_code = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "코드를 입력하세요"})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "password1",
            "password2",
            "nickname",
            "phone",
            "bank",
            "account_holder",
            "account_number",
            "recommender_code",
        ]


class LoginForm(forms.Form):
    username = forms.CharField(
        label="아이디",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "아이디를 입력하세요"}),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={"placeholder": "비밀번호를 입력하세요"}),
    )
