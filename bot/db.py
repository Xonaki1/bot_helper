"""Sync DB helpers called from async bot via asyncio.to_thread."""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import TelegramUser
from apps.tasks.models import Task, Category
from apps.shopping.models import ShoppingList, ShoppingItem


def get_or_create_user(telegram_id: int, username: str, first_name: str, last_name: str) -> TelegramUser:
    user, _ = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': username, 'first_name': first_name, 'last_name': last_name},
    )
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.save(update_fields=['username', 'first_name', 'last_name'])
    return user


def get_tasks(telegram_id: int, status: str | None = None):
    qs = Task.objects.filter(user__telegram_id=telegram_id).select_related('category')
    if status:
        qs = qs.filter(status=status)
    return list(qs)


def create_task(telegram_id: int, title: str, description: str, priority: str, due_date=None) -> Task:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    return Task.objects.create(
        user=user, title=title, description=description,
        priority=priority, due_date=due_date,
    )


def update_task_status(task_id: int, status: str) -> Task:
    task = Task.objects.get(pk=task_id)
    task.status = status
    task.save(update_fields=['status', 'updated_at'])
    return task


def delete_task(task_id: int) -> None:
    Task.objects.filter(pk=task_id).delete()


def get_task(task_id: int) -> Task:
    return Task.objects.select_related('category').get(pk=task_id)


def get_task_stats(telegram_id: int) -> dict:
    qs = Task.objects.filter(user__telegram_id=telegram_id)
    return {
        'total': qs.count(),
        'todo': qs.filter(status='todo').count(),
        'in_progress': qs.filter(status='in_progress').count(),
        'done': qs.filter(status='done').count(),
    }


#Shopping

def get_active_shopping_list(telegram_id: int) -> ShoppingList | None:
    return ShoppingList.objects.filter(
        user__telegram_id=telegram_id, is_archived=False
    ).prefetch_related('items').order_by('-created_at').first()


def create_shopping_list(telegram_id: int, name: str) -> ShoppingList:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    return ShoppingList.objects.create(user=user, name=name)


def add_shopping_item(list_id: int, name: str, quantity: str = '') -> ShoppingItem:
    shopping_list = ShoppingList.objects.get(pk=list_id)
    return ShoppingItem.objects.create(shopping_list=shopping_list, name=name, quantity=quantity)


def toggle_shopping_item(item_id: int, purchased: bool) -> ShoppingItem:
    item = ShoppingItem.objects.get(pk=item_id)
    item.is_purchased = purchased
    item.save(update_fields=['is_purchased'])
    return item


def delete_shopping_item(item_id: int) -> None:
    ShoppingItem.objects.filter(pk=item_id).delete()


def clear_purchased_items(list_id: int) -> int:
    deleted, _ = ShoppingItem.objects.filter(shopping_list_id=list_id, is_purchased=True).delete()
    return deleted


def get_shopping_list(list_id: int) -> ShoppingList:
    return ShoppingList.objects.prefetch_related('items').get(pk=list_id)


def archive_shopping_list(list_id: int) -> None:
    ShoppingList.objects.filter(pk=list_id).update(is_archived=True)
