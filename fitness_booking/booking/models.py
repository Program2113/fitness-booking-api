# Create your models here.
from django.db import models

class Class(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    available_slots = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.datetime}"

class Booking(models.Model):
    fitness_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()

    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name}"
