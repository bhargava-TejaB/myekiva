from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCreateViewSet, SchoolAdminViewSet, TeacherViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'users', UserCreateViewSet, basename='user')
router.register(r'school-admins', SchoolAdminViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
