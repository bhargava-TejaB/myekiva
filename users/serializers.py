from rest_framework import serializers
from .models import User, SchoolAdmin, Teacher, Student
from schools.models import School, Subject, Classroom
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_type = validated_data.get('user_type')  # Get user_type from validated_data
        password = validated_data.pop('password')
        school = self.context.get('school')  # Get school from context (passed from view)

        # Create the user without the user_type argument as it's already part of validated_data
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Handle user types: create related models (SchoolAdmin, Teacher, or Student)
        if user_type == 'schooladmin':
            SchoolAdmin.objects.create(user=user, school=school)
        elif user_type == 'teacher':
            Teacher.objects.create(user=user, school=school)
        elif user_type == 'student':
            Student.objects.create(user=user, school=school)

        return user

class SchoolAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SchoolAdmin
        fields = ['id', 'user', 'school']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        return SchoolAdmin.objects.create(user=user, **validated_data)

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested user serializer
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'school', 'contact_number', 'email', 'subjects']

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Extract user data
        user = User.objects.create_user(**user_data)  # Create the user
        subjects_data = validated_data.pop('subjects', [])  # Extract subjects data

        # Create teacher instance
        teacher = Teacher.objects.create(user=user, **validated_data)
        # Assign subjects using .set() instead of direct assignment
        teacher.subjects.set(subjects_data)

        return teacher

    def update(self, instance, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        
        # Update other fields using the parent class's update method
        instance = super().update(instance, validated_data)
        
        # Update the many-to-many relationship using .set()
        if subjects_data:
            instance.subjects.set(subjects_data)
        
        return instance
    
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested user serializer
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())  # Link to Classroom

    class Meta:
        model = Student
        fields = ['id', 'user', 'school', 'classroom', 'roll_number', 'date_of_birth', 'parent_name', 'parent_contact', 'joined_date', 'address', 'profile_picture']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)  # Create user instance
        student = Student.objects.create(user=user, **validated_data)  # Create student instance
        return student

    def update(self, instance, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        instance = super().update(instance, validated_data)
        instance.subjects.set(subjects_data)
        return instance

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)  # gets access and refresh tokens

        user = self.user
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
        }

        # Add school details based on user type
        if user.user_type == "student":
            try:
                student = Student.objects.select_related("school").get(user=user)
                data["school"] = {
                    "id": student.school.id,
                    "name": student.school.name
                }
            except Student.DoesNotExist:
                data["school"] = None

        elif user.user_type == "teacher":
            try:
                teacher = Teacher.objects.select_related("school").get(user=user)
                data["school"] = {
                    "id": teacher.school.id,
                    "name": teacher.school.name
                }
            except Teacher.DoesNotExist:
                data["school"] = None

        elif user.user_type == "schooladmin":
            try:
                school = School.objects.get(schooladmin__user=user)
                data["school"] = {
                    "id": school.id,
                    "name": school.name
                }
            except School.DoesNotExist:
                data["school"] = None

        else:
            data["school"] = None

        return data