from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'category', 'category_name', 'created_at', 'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user.telegram_profile
        return super().create(validated_data)
