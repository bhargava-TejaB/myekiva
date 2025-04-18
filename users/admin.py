from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, SchoolAdmin, Teacher, Student

# ----------------------------
# Custom Forms for User Admin
# ----------------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'user_type', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'user_type', 'first_name', 'last_name', 'is_active', 'is_staff')

# ----------------------------
# Custom User Admin
# ----------------------------
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('id', 'email', 'user_type', 'first_name', 'last_name', 'is_active')
    list_filter = ('user_type', 'is_active')
    ordering = ('id',)
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_type', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

# ----------------------------
# Custom Admins for Related Models
# ----------------------------
class SchoolAdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_user_type', 'get_user_name')

    def get_user_type(self, obj):
        return obj.user.user_type
    get_user_type.short_description = 'User Type'

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Name'

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_user_type', 'get_user_name')

    def get_user_type(self, obj):
        return obj.user.user_type
    get_user_type.short_description = 'User Type'

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Name'

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_user_type', 'get_user_name')

    def get_user_type(self, obj):
        return obj.user.user_type
    get_user_type.short_description = 'User Type'

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Name'

# ----------------------------
# Register All Models
# ----------------------------
admin.site.register(User, CustomUserAdmin)
admin.site.register(SchoolAdmin, SchoolAdminAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
