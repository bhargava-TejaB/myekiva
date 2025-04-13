from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='subjects')
    classrooms = models.ManyToManyField('schools.Classroom', related_name='subjects', blank=True)
    
    def __str__(self):
        return self.name
