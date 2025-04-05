from .permissions import IsSuperUser, IsSchoolAdmin
from rest_framework.exceptions import PermissionDenied
from schools.models import School
from .serializers import UserSerializer
from .models import User
from rest_framework import viewsets, permissions

class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.request.user.is_superuser:
            school_id = self.request.data.get('school_id')
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
    