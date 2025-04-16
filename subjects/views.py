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
from rest_framework.decorators import action

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school_id = self.request.query_params.get('school_id')
        if school_id:
            return Subject.objects.filter(school__id=school_id)
        return Subject.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        subject_id = data.get("id")
        name = data.get("name")
        school_id = data.get("school")
        classroom_ids = data.get("classroom_ids", [])

        # UPDATE flow if ID is present
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check for duplicate subject name in same school
            if Subject.objects.exclude(id=subject.id).filter(name__iexact=name, school_id=school_id).exists():
                return Response(
                    {"detail": f"Subject '{name}' already exists for this school."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subject.name = name
            subject.school_id = school_id
            subject.save()

            if classroom_ids:
                subject.classrooms.set(classroom_ids)

            serializer = self.get_serializer(subject)
            return Response(serializer.data)

        # CREATE flow
        if Subject.objects.filter(name__iexact=name, school_id=school_id).exists():
            return Response(
                {"detail": f"Subject '{name}' already exists for this school."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        subject = serializer.save()

        if classroom_ids:
            subject.classrooms.set(classroom_ids)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        name = request.data.get("name")
        school_id = request.data.get("school")
        print(request.data,'**'*100)
        # Prevent renaming to an existing subject in the same school
        if name and school_id:
            if Subject.objects.exclude(id=instance.id).filter(name__iexact=name, school_id=school_id).exists():
                return Response(
                    {"detail": f"Subject '{name}' already exists for this school."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        classroom_ids = request.data.pop("classroom_ids", None)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if classroom_ids is not None:
            instance.classrooms.set(classroom_ids)

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="details")
    def with_teachers(self, request, pk=None):
        subject = self.get_object()

        # Get all teachers teaching this subject
        teachers = subject.teachers.all()

        response_data = {
            "subject": subject.name,
            "teachers": [
                {"id": teacher.user.id, "name": teacher.user.get_full_name() or teacher.user.username}
                for teacher in teachers
            ]
        }
        return Response(response_data)

    
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
