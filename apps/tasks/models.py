from django.db import models
from apps.users.models import TelegramUser


class Category(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В процессе'
        DONE = 'done', 'Выполнено'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def status_emoji(self):
        return {'todo': '📋', 'in_progress': '⚙️', 'done': '✅'}[self.status]

    @property
    def priority_emoji(self):
        return {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[self.priority]
