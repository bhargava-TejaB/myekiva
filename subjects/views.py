from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import SubjectSerializer
from users.permissions import IsSuperUserOrSchoolAdmin
from users.models import Student, Teacher
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from users.models import School, Subject

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOrSchoolAdmin]

    def get_queryset(self):
        school_id = self.request.query_params.get('school_id')
        if school_id:
            return Subject.objects.filter(school__id=school_id)
        return Subject.objects.all()
    
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
