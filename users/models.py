from django.contrib.auth.models import AbstractUser
from django.db import models
from schools.models import School

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('schooladmin', 'School Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # keep username for compatibility

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom = models.CharField(max_length=100)  # or FK to Classroom
    roll_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_contact = models.CharField(max_length=15)
    joined_date = models.DateField()
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subjects_taught = models.TextField(blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class SchoolAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.OneToOneField(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - Admin"
