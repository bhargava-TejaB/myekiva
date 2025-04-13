from rest_framework import serializers
from .models import Subject
from schools.models import Classroom

class SubjectSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Classroom.objects.all(),
        write_only=True
    )
    classroom_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'school', 'classrooms', 'classroom_names']

    def get_classroom_names(self, obj):
        return [classroom.name for classroom in obj.classrooms.all()]
