from django.contrib import admin
from .models import User, SchoolAdmin, Teacher, Student

admin.site.register(User)
admin.site.register(SchoolAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
