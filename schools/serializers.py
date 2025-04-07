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
