from .permissions import IsSuperUser, IsSchoolAdmin
from rest_framework.exceptions import PermissionDenied
from schools.models import School
from .serializers import UserSerializer, SchoolAdminSerializer, TeacherSerializer, StudentSerializer, MyTokenObtainPairSerializer
from .models import User, SchoolAdmin, Teacher, Student
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated 
from django.db import models
from rest_framework_simplejwt.views import TokenObtainPairView
import logging

logger = logging.getLogger(__name__)

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user_type = self.request.data.get('user_type')

        if self.request.user.is_superuser:
            school_id = self.request.data.get('school_id')
            if not school_id:
                raise serializers.ValidationError("Superuser must provide school_id.")
            context['school'] = School.objects.get(id=school_id)

        elif hasattr(self.request.user, 'schooladmin'):
            context['school'] = self.request.user.schooladmin.school

        return context

    def create(self, request, *args, **kwargs):
        user_type = request.data.get("user_type")

        if request.user.is_superuser:
            if user_type not in ["schooladmin", "teacher", "student"]:
                raise PermissionDenied("Invalid user type.")
        elif request.user.user_type == "schooladmin":
            if user_type not in ["teacher", "student"]:
                raise PermissionDenied("SchoolAdmin can only create Teacher or Student.")
        else:
            raise PermissionDenied("You don't have permission to create users.")

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        elif hasattr(self.request.user, 'schooladmin'):
            return User.objects.filter(
                models.Q(schooladmin__school=self.request.user.schooladmin.school) |
                models.Q(teacher__school=self.request.user.schooladmin.school) |
                models.Q(student__school=self.request.user.schooladmin.school)
            ).distinct()
        else:
            return User.objects.none()

class SchoolAdminViewSet(viewsets.ModelViewSet):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

# ViewSet to create and manage students
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request.user, 'schooladmin'):
            context['school'] = self.request.user.schooladmin.school
        return context

    def get_queryset(self):
        queryset = self.queryset

        # Restrict to school admin's school
        if hasattr(self.request.user, 'schooladmin'):
            queryset = queryset.filter(school=self.request.user.schooladmin.school)

        # ✅ Filter by classroom and section if provided
        classroom_id = self.request.query_params.get('classroom_id')
        section_id = self.request.query_params.get('section_id')

        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        return queryset

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to create students.")

        if hasattr(request.user, 'schooladmin'):
            school_id = request.data.get('school')
            if not school_id or int(school_id) != request.user.schooladmin.school.id:
                raise PermissionDenied("You can only create students for your own school.")
        
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to update students.")

        if hasattr(request.user, 'schooladmin') and student.school != request.user.schooladmin.school:
            raise PermissionDenied("You can only update students for your own school.")
        
        return super().update(request, *args, **kwargs)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer