from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCreateViewSet, SchoolAdminViewSet, TeacherViewSet, StudentViewSet, MyTokenObtainPairView

router = DefaultRouter()
router.register(r'users', UserCreateViewSet, basename='user')
router.register(r'school-admins', SchoolAdminViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('tokens/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
