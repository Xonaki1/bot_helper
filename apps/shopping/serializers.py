from rest_framework import serializers
from .models import ShoppingList, ShoppingItem


class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        fields = ('id', 'name', 'quantity', 'is_purchased', 'created_at')
        read_only_fields = ('created_at',)


class ShoppingListSerializer(serializers.ModelSerializer):
    items = ShoppingItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    purchased_items = serializers.ReadOnlyField()

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'is_archived', 'total_items', 'purchased_items', 'items', 'created_at')
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user.telegram_profile
        return super().create(validated_data)
