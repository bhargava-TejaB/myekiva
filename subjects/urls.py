from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, SchoolStatsView

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('school_stats', SchoolStatsView.as_view(), name='school-stats'),
]
