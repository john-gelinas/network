from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    text = models.TextField(max_length=1000)
    title = models.CharField(max_length=100)


class Like(models.Model):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,  # if user is deleted, delete likes associated
        related_name="like",
    )
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,  # if post is deleted, delete likes associated
        related_name="like",
    )

class Follower:
    following = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,  # if user is deleted, delete follower associated
        related_name="following",
    )
    follower = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,  # if user is deleted, delete follower associated
        related_name="follower",
    )