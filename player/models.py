from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    DateTimeField,
    ForeignKey,
    OneToOneField,
)
from django.db.models.signals import post_save

from explore.models import Area

class Player(models.Model):
    user = OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    location = ForeignKey(Area, null=True, on_delete=models.SET_NULL)
    last_active = DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)

    def user_save(sender, instance, **kwargs):
        if kwargs['created']:
            player = Player(user=instance)
            player.save()

post_save.connect(Player.user_save, sender=User)
