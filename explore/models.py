from django.conf import settings
from django.db import models
from django.db.models import CharField, DateTimeField, ForeignKey, TextField

# Create your models here.

class Area(models.Model):

    created_at = DateTimeField(auto_now_add=True)
    creator = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    title = CharField(max_length=512)
    description = TextField()

    def __str__(self):
        return self.title

class Activity(models.Model):

    created_at = DateTimeField(auto_now_add=True)
    activity_text = CharField(max_length=512)
    area = ForeignKey(Area, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity_text

