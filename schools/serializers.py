from rest_framework import serializers
from .models import School, Classroom, Section
from subjects.models import Subject
from users.models import Teacher

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id','name']

class ClassroomSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True)
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'grade', 'school', 'sections']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        classroom = Classroom.objects.create(**validated_data)

        for section_data in sections_data:
            Section.objects.create(classroom=classroom, **section_data)

        return classroom

class SubjectWithClassesSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'classes']

    def get_classes(self, obj):
        # Get the school_id from the context
        school_id = self.context.get('school_id')

        # If school_id is not provided in context, return an empty list
        if not school_id:
            return []

        # Fetch classrooms related to this subject and filter by school_id
        classrooms = obj.classrooms.filter(school__id=school_id)

        # Collect unique grades for this subject
        unique_grades = []
        for classroom in classrooms:
            # Only add unique grades for this subject and school
            if classroom.grade not in [item['grade'] for item in unique_grades]:
                unique_grades.append({'id': classroom.id, 'grade': classroom.grade})

        return unique_grades