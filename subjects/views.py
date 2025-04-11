from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Subject
from .serializers import SubjectSerializer
from users.permissions import IsSuperUserOrSchoolAdmin

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOrSchoolAdmin]

    def get_queryset(self):
        school_id = self.request.query_params.get('school_id')
        if school_id:
            return Subject.objects.filter(school__id=school_id)
        return Subject.objects.all()
