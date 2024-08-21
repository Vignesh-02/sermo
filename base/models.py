from django.db import models
from django.contrib.auth.models import AbstractUser


# this is the defult user model
# from django.contrib.auth.models import User


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    # ImageField uses a 3rd party package called Pillow
    avatar = models.ImageField(null=True, default="avatar.svg")    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

# a room can have only 1 topic but multiple messagews
class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # auto now add saves the time when the record was initially created

    class Meta:
        ordering = ['-updated', '-created']


    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # models.CASCADE means that if a room is deleted, delete the messages too
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.body[0:50]