from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    OneToOneField,
    TextField,
)
from django.db.models.signals import post_save

# Create your models here.

class News(models.Model):
    created_at = DateTimeField(auto_now_add=True)
    text = TextField(blank=True, default='')

    def __str__(self):
        return self.text

class Area(models.Model):

    created_at = DateTimeField(auto_now_add=True)
    creator = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    title = CharField(max_length=512)
    description = TextField(blank=True, default='')
    published = BooleanField(default=False)

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

    def tidy(user, area):
        Activity.objects.filter(creator_only=True, creator=user).exclude(area=area).delete()

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

class Score(models.Model):
    user = OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        on_delete=models.CASCADE)
    total = IntegerField(default=0)

    def user_save(sender, instance, **kwargs):
        try:
            Score.objects.get(user=instance)
        except ObjectDoesNotExist:
            Score(user=instance).save()
	
# Ensure each user has a score entry
post_save.connect(Score.user_save, sender=User)
