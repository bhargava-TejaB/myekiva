from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from schools.models import School, Classroom, Section
from subjects.models import Subject

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Keep username = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # this hashes password properly
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Optional: Auto-assign username for superusers
        if not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('superuser', 'Super User'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('schooladmin', 'School Admin'),
    )
    
    # Fields
    username = models.CharField(max_length=150, unique=True, blank=True)  # Make username blank as it will be auto-generated
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)  # already in AbstractUser
    last_name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Custom manager
    objects = CustomUserManager()
    
    # Django specific fields
    USERNAME_FIELD = 'email'  # used for login
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']  # Username will be auto-generated

    def __str__(self):
        return f"{self.email} ({self.user_type})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
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
