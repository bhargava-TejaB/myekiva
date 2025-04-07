from django.db import models

class School(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    partnership_date = models.DateField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    schools = models.ManyToManyField('School', related_name='subjects', blank=True)  # Many-to-many relationship with School

    def __str__(self):
        return self.name

# models.py (in your 'school' app)

class Classroom(models.Model):
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=50)  # e.g., "Grade 5", "Grade 10"
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name="classrooms", blank=True)  # subjects taught in the classroom
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE)  # Teacher for this classroom

    def __str__(self):
        return f"{self.name} - {self.grade} ({self.school.name})"

