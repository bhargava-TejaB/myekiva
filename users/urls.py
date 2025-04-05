from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCreateViewSet

router = DefaultRouter()
router.register(r'users', UserCreateViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
