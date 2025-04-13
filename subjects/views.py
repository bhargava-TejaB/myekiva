from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import SubjectSerializer
from users.permissions import IsSuperUserOrSchoolAdmin
from users.models import Student, Teacher
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from users.models import School, Subject

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOrSchoolAdmin]

    def get_queryset(self):
        school_id = self.request.query_params.get('school_id')
        if school_id:
            return Subject.objects.filter(school__id=school_id)
        return Subject.objects.all()

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        school_id = request.data.get("school")

        # Check if subject with same name and school exists
        if Subject.objects.filter(name__iexact=name, school_id=school_id).exists():
            return Response(
                {"detail": f"Subject '{name}' already exists for this school."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        name = request.data.get("name")
        school_id = request.data.get("school")

        # Prevent renaming to an existing subject in the same school
        if name and school_id:
            if Subject.objects.exclude(id=instance.id).filter(name__iexact=name, school_id=school_id).exists():
                return Response(
                    {"detail": f"Subject '{name}' already exists for this school."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Extract classrooms separately to update manually later
        classrooms = request.data.pop("classrooms", None)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Update classrooms if provided
        if classrooms is not None:
            instance.classrooms.set(classrooms)

        return Response(serializer.data)

    
class SchoolStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        school_id = request.query_params.get('school_id')
        if not school_id:
            raise NotFound("school_id is required.")

        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            raise NotFound("School not found.")

        student_count = Student.objects.filter(school_id=school_id).count()
        teacher_count = Teacher.objects.filter(school_id=school_id).count()
        subject_count = Subject.objects.filter(school_id=school_id).count()

        return Response({
            "school": {
                "id": school.id,
                "name": school.name,
            },
            "school_stats": {
                "total_students": student_count,
                "total_teachers": teacher_count,
                "total_subjects": subject_count,
                "pending_reviews": 9  # Customize as needed
            }
        })
