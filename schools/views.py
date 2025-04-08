from rest_framework import viewsets, permissions
from .models import School, Subject, Classroom
from .serializers import SchoolSerializer, SubjectSerializer, ClassroomSerializer
from users.permissions import IsSuperUserOrSchoolAdmin, IsSuperUser
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Student

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
    
class ClassroomStudentCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, school_id):
        classrooms = Classroom.objects.filter(school_id=school_id)
        data = []

        for classroom in classrooms:
            student_count = Student.objects.filter(classroom=classroom).count()
            data.append({
                "classroom_id": classroom.id,
                "name": classroom.name,
                "grade": classroom.grade,
                "student_count": student_count
            })

        return Response(data) 