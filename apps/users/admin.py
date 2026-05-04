from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'username', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    readonly_fields = ('telegram_id', 'created_at')
