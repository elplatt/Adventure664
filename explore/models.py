from django.conf import settings
from django.db import models
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    TextField,
)

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
    creator = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL)
    activity_text = CharField(max_length=512)
    area = ForeignKey(Area, null=True, on_delete=models.CASCADE)
    creator_only = BooleanField(default=False)

    def __str__(self):
        return self.activity_text

class Connection(models.Model):
    created_at = DateTimeField(auto_now_add=True)
    creator = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL)
    area_from = ForeignKey(Area, on_delete=models.CASCADE, related_name='outgoing')
    area_to = ForeignKey(Area, on_delete=models.CASCADE, related_name='incoming')
    title = CharField(max_length=512)

    def __str__(self):
        return f'{self.area_from.id} : {self.title} -> {self.area_to.id})'
