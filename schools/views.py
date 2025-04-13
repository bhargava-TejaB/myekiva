from rest_framework import viewsets, permissions as drf_permissions
from .models import School, Classroom, Section
from subjects.models import Subject
from .serializers import SchoolSerializer, ClassroomSerializer, SubjectWithClassesSerializer, SectionSerializer
from subjects.serializers import SubjectSerializer
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

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all().order_by('grade')
    serializer_class = ClassroomSerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsSuperUserOrSchoolAdmin]

    def get_queryset(self):
        school_id = self.request.query_params.get('school_id')
        if school_id:
            return Classroom.objects.filter(school__id=school_id)
        return Classroom.objects.all()

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        grade = request.data.get("grade")
        school_id = request.data.get("school")

        # Check if a classroom with the same name and grade already exists in the same school
        if Classroom.objects.filter(name=name, grade=grade, school_id=school_id).exists():
            return Response(
                {"detail": f"Classroom '{name}' with grade '{grade}' already exists in this school."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If no duplicates, proceed with creating the classroom using the serializer
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Get the updated data from the request
        name = request.data.get("name")
        grade = request.data.get("grade")
        school_id = request.data.get("school")

        # Check for duplicate classroom with the same name, grade, and school (excluding the current classroom)
        if Classroom.objects.exclude(id=instance.id).filter(name=name, grade=grade, school_id=school_id).exists():
            return Response(
                {"detail": f"Classroom '{name}' with grade '{grade}' already exists in this school."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle updating the sections (M2M field) directly here in the viewset
        sections_data = request.data.get("sections")
        if sections_data is not None:
            # Handle removing and adding sections as required
            section_ids = [section["id"] for section in sections_data]
            instance.sections.set(section_ids)

        # Proceed with updating the classroom and any other data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
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
        print(subjects,'***'*12)
        # Pass school_id to the serializer context
        serializer = SubjectWithClassesSerializer(subjects, many=True, context={'school_id': school_id})

        return Response(serializer.data, status=status.HTTP_200_OK)