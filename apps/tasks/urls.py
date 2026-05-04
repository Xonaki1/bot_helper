from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet

router = DefaultRouter()
router.register('', TaskViewSet, basename='task')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
