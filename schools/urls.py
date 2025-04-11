from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, ClassroomViewSet, ClassroomStudentCountView, SubjectWithClassesView, SectionViewSet
from django.urls import path, include
from subjects.views import SubjectViewSet

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'sections', SectionViewSet, basename='section')

urlpatterns = [
    path('', include(router.urls)),
    path('school/<int:school_id>/classrooms/', ClassroomStudentCountView.as_view(), name='classroom-student-count'),
    path('subjects-with-classes', SubjectWithClassesView.as_view(), name='subjects_with_classes_by_school'),
]