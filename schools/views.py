from rest_framework import viewsets, permissions
from .models import School, Subject, Classroom
from .serializers import SchoolSerializer, SubjectSerializer, ClassroomSerializer
from users.permissions import IsSuperUserOrSchoolAdmin, IsSuperUser

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrSchoolAdmin]

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser and not hasattr(request.user, 'schooladmin'):
            raise PermissionDenied("You don't have permission to create classrooms.")

        # Ensure the classroom is being created for the correct school
        school_id = request.data.get('school')
        if int(school_id) != request.user.schooladmin.school.id:
            raise PermissionDenied("You can only create classrooms for your own school.")
        
        # Now proceed with the regular creation
        return super().create(request, *args, **kwargs)