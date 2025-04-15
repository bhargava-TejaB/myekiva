from rest_framework import serializers
from .models import Subject
from schools.models import Classroom

class SubjectSerializer(serializers.ModelSerializer):
    # Accepts classroom IDs for input
    classroom_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Classroom.objects.all(),
        write_only=True,
        source="classrooms"
    )

    # Returns classroom info in {value, label} format
    classrooms = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'school', 'classroom_ids', 'classrooms']

    def get_classrooms(self, obj):
        return [
            {"value": classroom.id, "label": classroom.name}
            for classroom in obj.classrooms.all()
        ]
    
