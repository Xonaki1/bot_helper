from rest_framework.routers import DefaultRouter
from .views import ShoppingListViewSet, ShoppingItemViewSet

router = DefaultRouter()
router.register('lists', ShoppingListViewSet, basename='shopping-list')
router.register('items', ShoppingItemViewSet, basename='shopping-item')

urlpatterns = router.urls
