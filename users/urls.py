from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, StudentViewSet

# Create a router for our viewsets
router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'students', StudentViewSet, basename='student')

# Include the router URLs
urlpatterns = [
    path('', include(router.urls)),  # This includes all ViewSet-generated routes
]