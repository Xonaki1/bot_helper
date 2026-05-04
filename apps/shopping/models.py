from django.db import models
from apps.users.models import TelegramUser


class ShoppingList(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='shopping_lists')
    name = models.CharField(max_length=255, default='Список покупок')
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user})'

    @property
    def total_items(self):
        return self.items.count()

    @property
    def purchased_items(self):
        return self.items.filter(is_purchased=True).count()


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=50, blank=True, default='')
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'
        ordering = ['is_purchased', 'created_at']

    def __str__(self):
        qty = f' ({self.quantity})' if self.quantity else ''
        return f'{self.name}{qty}'
