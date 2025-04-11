from rest_framework import serializers
from .models import User, SchoolAdmin, Teacher, Student
from schools.models import School, Classroom, Section
from subjects.models import Subject
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',  'first_name', 'last_name', 'user_type', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
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
        fields = ['id', 'user','school']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        return SchoolAdmin.objects.create(user=user, **validated_data)

class ClassroomSectionMapField(serializers.ListField):
    def to_internal_value(self, data):
        # Ensure input data is a list of dictionaries
        if not isinstance(data, list):
            raise serializers.ValidationError("classroom_section_map must be a list of mappings.")
        
        result = []
        for mapping in data:
            if not isinstance(mapping, dict):
                raise serializers.ValidationError("Each mapping must be a dictionary.")
            
            classroom_id = mapping.get("classroom")
            section_ids = mapping.get("sections")

            if not isinstance(classroom_id, int):
                raise serializers.ValidationError("Classroom ID must be an integer.")
            
            if not isinstance(section_ids, list) or not all(isinstance(s, int) for s in section_ids):
                raise serializers.ValidationError("Sections must be a list of integers.")

            result.append({
                "classroom": classroom_id,
                "sections": section_ids
            })
        
        return result


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    classroom_section_map = ClassroomSectionMapField(write_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'school', 'subjects', 'classroom_section_map']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subjects_data = validated_data.pop('subjects', [])
        classroom_section_map = validated_data.pop('classroom_section_map', [])

        # Create User
        username = user_data.get('username', user_data['email'])
        user = User.objects.create_user(
            username=username,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=f"pass1234@{user_data['first_name'].lower()}",
            user_type=user_data['user_type'],
            phone_number=user_data.get('phone_number', None)
        )

        teacher = Teacher.objects.create(user=user, **validated_data)

        # Set subjects
        teacher.subjects.set(subjects_data)

        classrooms = []
        sections = []

        for mapping in classroom_section_map:
            classroom_id = mapping["classroom"]
            section_ids = mapping["sections"]

            try:
                classroom = Classroom.objects.get(id=classroom_id)
                classrooms.append(classroom)
            except Classroom.DoesNotExist:
                raise serializers.ValidationError(f"Classroom with ID {classroom_id} does not exist.")

            for sec_id in section_ids:
                try:
                    section = Section.objects.get(id=sec_id, classroom=classroom)
                    sections.append(section)
                except Section.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Section with ID {sec_id} does not belong to Classroom {classroom_id}."
                    )

        teacher.classrooms.set(classrooms)
        teacher.sections.set(sections)

        return teacher

    
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
        data = super().validate(attrs)

        user = self.user
        data['user'] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
        }

        school_data = None
        student_count = 0
        teacher_count = 0
        class_count = 0

        if user.user_type == "student":
            try:
                student = Student.objects.select_related("school").get(user=user)
                school = student.school
                school_data = {"id": school.id, "name": school.name}
            except Student.DoesNotExist:
                pass

        elif user.user_type == "teacher":
            try:
                teacher = Teacher.objects.select_related("school").get(user=user)
                school = teacher.school
                school_data = {"id": school.id, "name": school.name}
            except Teacher.DoesNotExist:
                pass

        elif user.user_type == "schooladmin":
            try:
                school = School.objects.get(schooladmin__user=user)
                school_data = {"id": school.id, "name": school.name}
            except School.DoesNotExist:
                pass

        # If we found the school, fetch counts
        if school_data:
            school_id = school_data["id"]
            student_count = Student.objects.filter(school_id=school_id).count()
            teacher_count = Teacher.objects.filter(school_id=school_id).count()
            class_count = Classroom.objects.filter(school_id=school_id).count()

        data["school"] = school_data
        data["school_stats"] = {
            "total_students": student_count,
            "total_teachers": teacher_count,
            "total_subjects": class_count,
            "pending_reviews": 9
        }

        return data