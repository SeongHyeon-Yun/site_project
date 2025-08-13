from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 목록 컬럼
    list_display = (
        "username",
        "email",
        "nickname",
        "phone",
        "bank",
        "account_holder",
        "account_number",
        "recommender_code",
        "is_staff",
        "is_active",
    )
    list_display_links = ("username",)
    search_fields = (
        "username",
        "email",
        "nickname",
        "phone",
        "account_number",
        "recommender_code",
    )
    list_filter = ("is_staff", "is_active", "bank")
    ordering = ("-date_joined",)
    list_per_page = 50

    # 상세/수정 페이지 필드 구성
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("개인 정보", {"fields": ("email", "nickname", "phone")}),
        (
            "계좌 정보",
            {
                "fields": (
                    "bank",
                    "account_holder",
                    "account_number",
                    "recommender_code",
                )
            },
        ),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("중요 일자", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined")

    # 새 사용자 추가 페이지 필드 구성
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "nickname",
                    "phone",
                    "bank",
                    "account_holder",
                    "account_number",
                    "recommender_code",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )
