from .permissions import IsSuperUser, IsSchoolAdmin
from rest_framework.exceptions import PermissionDenied
from schools.models import School
from .serializers import UserSerializer, SchoolAdminSerializer, TeacherSerializer, StudentSerializer, MyTokenObtainPairSerializer
from .models import User, SchoolAdmin, Teacher, Student
from rest_framework import viewsets, permissions
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

class SchoolAdminViewSet(viewsets.ModelViewSet):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request.user, 'schooladmin'):
            context['school'] = self.request.user.schooladmin.school
        return context

    def create(self, request, *args, **kwargs):
        print("ii"*100)
        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to create teachers.")
        print("xx"*100)
        if hasattr(request.user, 'schooladmin'):
            school_id = request.data.get('school')
            if int(school_id) != request.user.schooladmin.school.id:
                raise PermissionDenied("You can only create teachers for your own school.")
        print("yy"*100)
        print(request.data.get('school'))
        print(request.data.get('user'))
        print('c'*100)
        logger.debug(f"Request data: {request.data}")
        print("yy"*100)
        print(request.data)
        return super().create(request, *args, **kwargs)

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

    def create(self, request, *args, **kwargs):
        # Only superuser or school admin can create students
        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to create students.")

        if hasattr(request.user, 'schooladmin'):
            school_id = request.data.get('school')
            if int(school_id) != request.user.schooladmin.school.id:
                raise PermissionDenied("You can only create students for your own school.")
        
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Ensure only superuser or school admin can update students
        student = self.get_object()

        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to update students.")

        if hasattr(request.user, 'schooladmin') and student.school != request.user.schooladmin.school:
            raise PermissionDenied("You can only update students for your own school.")

        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        # If the user is a school admin, only return students for their school
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            return self.queryset.filter(school=school)
        return self.queryset  # For superuser, return all students

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer