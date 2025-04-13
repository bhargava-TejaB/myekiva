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

class Classroom(models.Model):
    name = models.CharField(max_length=255) #Class 10
    grade = models.CharField(max_length=50)  # e.g., "10", "9"
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    

class Section(models.Model):
    name = models.CharField(max_length=100)  # e.g., "A", "B"
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f"{self.classroom.name} - {self.name}"
