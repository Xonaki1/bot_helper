from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        tg_user = getattr(self.request.user, 'telegram_profile', None)
        if tg_user:
            return Task.objects.filter(user=tg_user).select_related('category')
        return Task.objects.none()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        tg_user = getattr(self.request.user, 'telegram_profile', None)
        if tg_user:
            return Category.objects.filter(user=tg_user)
        return Category.objects.none()
