from rest_framework import serializers
from .models import School, Classroom, Section
from subjects.models import Subject
from users.models import Teacher

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'name', 'student_count']

    def get_student_count(self, section):
        return section.student_set.count()


class ClassroomSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True)  # Nested serializer for sections
    student_count = serializers.SerializerMethodField(read_only=True)  # Student count field

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'grade', 'school', 'sections', 'student_count']  # Define necessary fields

    def get_student_count(self, classroom):
        # Returns the student count for the classroom
        return classroom.student_set.count()

    def create(self, validated_data):
        # Handle sections data in case of classroom creation
        sections_data = validated_data.pop('sections', [])
        classroom = Classroom.objects.create(**validated_data)

        # Create and associate sections with the classroom
        for section_data in sections_data:
            Section.objects.create(classroom=classroom, **section_data)
        
        return classroom

    def update(self, instance, validated_data):
        # Handle the update of sections (M2M field)
        sections_data = validated_data.pop('sections', None)

        # Update the classroom instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If sections data is provided, update the sections
        if sections_data is not None:
            section_ids = [section['id'] for section in sections_data]
            instance.sections.set(section_ids)

        return instance

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