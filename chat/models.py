from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Group(models.Model):
    name = models.CharField( max_length=100)
    def __str__(self):
        return self.name
    
class Chat(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE)
    def __str__(self):
        return self.content
    