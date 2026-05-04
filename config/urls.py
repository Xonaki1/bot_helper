from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/shopping/', include('apps.shopping.urls')),
    path('webhook/', include('apps.users.webhook_urls')),
]
