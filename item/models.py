from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    CharField,
    DateTimeField,
    ForeignKey,
    TextField,
)
from django.db.models.signals import post_save
from explore.models import Area
class Item(models.Model):

    title = CharField(max_length=64)
    short_description = CharField(max_length=256)
    long_description = TextField()
    location = ForeignKey(Area, null=True, on_delete=models.SET_NULL)
    creator = ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
