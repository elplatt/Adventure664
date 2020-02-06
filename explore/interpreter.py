from django.urls import reverse
from .models import Activity

class Interpreter(object):

    def __init__(self, models):
        # Save models
        self.models = models

    def execute(self, command):

        # Parse command into words
        words = command.split(' ')
        if len(words) > 0:
            operator = words[0]
        if len(words) > 1:
            target = words[1]

        # Determine type of command
        if operator == 'edit':
            if target == 'description':
                return reverse('explore:area_description', args=[self.models['area'].id])

        # If no command, leave a message
        activity_text = f'{self.models["user"].username}: {command}'
        activity = Activity(
            creator=self.models['user'],
            area=self.models['area'],
            activity_text=activity_text)
        activity.save()
