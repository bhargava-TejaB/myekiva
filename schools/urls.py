from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SubjectViewSet, ClassroomViewSet

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')

urlpatterns = router.urls
