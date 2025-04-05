from rest_framework import serializers
from .models import User, SchoolAdmin, Teacher, Student
from schools.models import School


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        password = validated_data.pop('password')
        school = self.context.get('school')  # passed from view

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user_type == 'schooladmin':
            SchoolAdmin.objects.create(user=user, school=school)
        elif user_type == 'teacher':
            Teacher.objects.create(user=user, school=school)
        elif user_type == 'student':
            Student.objects.create(user=user, school=school)

        return user
