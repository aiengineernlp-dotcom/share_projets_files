from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE) # CASCADE veut dire que: si l'utilisateur supprime le User account, le Profile aussi le sera.
    image = models.ImageField(default="profilepic.png",upload_to='profile_pictures')
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username}"
