from rest_framework import viewsets, permissions as drf_permissions
from .models import School, Subject, Classroom
from .serializers import SchoolSerializer, SubjectSerializer, ClassroomSerializer, SubjectWithClassesSerializer
from rest_framework import status
from users.permissions import IsSuperUserOrSchoolAdmin, IsSuperUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from users.models import Student
from users import permissions

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsSuperUser]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsSuperUserOrSchoolAdmin]

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [drf_permissions.IsAuthenticated]  # Ensure only authenticated users can access

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
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsSuperUserOrSchoolAdmin]

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

class SubjectWithClassesView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated]
    def get(self, request):
        school_id = request.query_params.get('school_id')  # Get the school_id from query parameters
        
        # If no school_id is provided, return an error
        if not school_id:
            return Response({"error": "school_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the subjects related to the classrooms for the given school_id
        subjects = Subject.objects.filter(classrooms__school__id=school_id).distinct()

        # Pass school_id to the serializer context
        serializer = SubjectWithClassesSerializer(subjects, many=True, context={'school_id': school_id})

        return Response(serializer.data, status=status.HTTP_200_OK)