from django.urls import path
from .webhook_view import TelegramWebhookView

urlpatterns = [
    path('', TelegramWebhookView.as_view(), name='telegram-webhook'),
]
