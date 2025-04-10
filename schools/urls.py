from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SubjectViewSet, ClassroomViewSet, ClassroomStudentCountView, SubjectWithClassesView
from django.urls import path, include

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')

urlpatterns = [
    path('', include(router.urls)),
    path('school/<int:school_id>/classrooms/', ClassroomStudentCountView.as_view(), name='classroom-student-count'),
    path('subjects-with-classes/', SubjectWithClassesView.as_view(), name='subjects_with_classes_by_school'),
]
