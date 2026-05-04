from django.contrib import admin
from .models import ShoppingList, ShoppingItem


class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 1
    fields = ('name', 'quantity', 'is_purchased')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'total_items', 'purchased_items', 'is_archived', 'created_at')
    list_filter = ('is_archived',)
    search_fields = ('name', 'user__username', 'user__first_name')
    list_editable = ('is_archived',)
    inlines = [ShoppingItemInline]
    readonly_fields = ('created_at',)


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'shopping_list', 'is_purchased', 'created_at')
    list_filter = ('is_purchased',)
    search_fields = ('name', 'shopping_list__name')
    list_editable = ('is_purchased',)
