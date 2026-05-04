from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ShoppingList, ShoppingItem
from .serializers import ShoppingListSerializer, ShoppingItemSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer

    def get_queryset(self):
        tg_user = getattr(self.request.user, 'telegram_profile', None)
        if tg_user:
            return ShoppingList.objects.filter(user=tg_user).prefetch_related('items')
        return ShoppingList.objects.none()

    @action(detail=True, methods=['post'])
    def clear_purchased(self, request, pk=None):
        shopping_list = self.get_object()
        shopping_list.items.filter(is_purchased=True).delete()
        return Response({'status': 'ok'})


class ShoppingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingItemSerializer

    def get_queryset(self):
        return ShoppingItem.objects.filter(
            shopping_list__user__telegram_id=self.request.query_params.get('tg_id')
        )
