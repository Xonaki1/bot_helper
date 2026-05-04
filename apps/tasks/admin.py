from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username', 'user__first_name')
    list_filter = ('user',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'user__username', 'user__first_name')
    list_editable = ('status', 'priority')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Статус и приоритет', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
