from django.contrib.auth.models import AbstractUser
from django.db import models
from schools.models import School, Classroom, Section
from subjects.models import Subject

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('schooladmin', 'School Admin'),
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)  # already in AbstractUser
    last_name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    USERNAME_FIELD = 'email'  # used for login
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    def __str__(self):
        return f"{self.email} ({self.user_type})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_contact = models.CharField(max_length=15)
    joined_date = models.DateField()
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name 

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, blank=True)
    classrooms = models.ManyToManyField(Classroom, blank=True)
    sections = models.ManyToManyField(Section, blank=True)
    
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name +   " - " + self.user.user_type

class SchoolAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.OneToOneField(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name}" + self.user.last_name + " - " + self.user.user_type
