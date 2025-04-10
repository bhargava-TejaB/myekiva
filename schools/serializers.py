from rest_framework import serializers
from .models import School, Subject, Classroom
from users.models import Teacher

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'schools']

class ClassroomSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'grade', 'school', 'subjects', 'teacher']

    def create(self, validated_data):
        # Extract subjects and teacher
        subjects_data = validated_data.pop('subjects', [])
        teacher_data = validated_data.pop('teacher', None)
        # Check if teacher is provided
        if not teacher_data:
            raise ValidationError("Teacher is required for creating a classroom.")
        
        # Create the Classroom instance
        classroom = Classroom.objects.create(teacher = teacher_data,**validated_data)

        # Assign the subjects (many-to-many field)
        classroom.subjects.set(subjects_data)

        classroom.save()

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