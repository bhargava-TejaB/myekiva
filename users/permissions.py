from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsSchoolAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'schooladmin'


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'teacher'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'student'
