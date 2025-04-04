from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, ClassViewSet, SubjectViewSet, CurriculumViewSet, TopicViewSet

router = DefaultRouter()
router.register(r'', SchoolViewSet, basename='school')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'curriculums', CurriculumViewSet, basename='curriculum')
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', include(router.urls))
]
