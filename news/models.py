from django.db import models
from django.contrib.auth.models import User

class Source(models.Model):
    sourceName = models.CharField(max_length = 50)
    image = models.ImageField(default='default.jpg', upload_to='source_pics')
    sourceType = models.CharField(max_length = 50)

    def __str__(self):
        return self.sourceName

class UserSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sources = models.ForeignKey(Source, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
