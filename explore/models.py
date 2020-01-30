from django.db import models
from django.db.models import CharField, DateTimeField

# Create your models here.

class Activity(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    activity_text = CharField(max_length=512)

    def __str__(self):
        return self.activity_text
