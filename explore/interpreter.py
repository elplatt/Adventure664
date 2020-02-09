from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from .models import Activity

class Interpreter(object):

    ALLOWED_CONNECTIONS = [
        'north',
        'south',
        'east',
        'west',
        'up',
        'down'
    ]

    def __init__(self, models):
        # Save models
        self.models = models

    def execute(self, command):

        # Parse command into words
        command = command.strip().lower()
        words = command.split(' ')
        if len(words) > 0:
            operator = words[0].strip().lower()
        if len(words) > 1:
            target = words[1].strip().lower()

        # Determine type of command
        if operator == 'create':
            if target == 'connection':
                title = ' '.join(words[2:]).strip().lower()
                if Interpreter.validate_connection(title):
                    kwargs = {
                        'source_id': self.models['area'].id,
                        'title': title,
                    }
                    return reverse('explore:new_connection', kwargs=kwargs)
                else:
                    activity = Activity(
                        area=self.models['area'],
                        creator=self.models['user'],
                        creator_only=True,
                        activity_text='Connections must be one of: ' + ', '.join(Interpreter.ALLOWED_CONNECTIONS) + '.',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])
        elif operator == 'edit':
            if target == 'description':
                return reverse('explore:area_description', args=[self.models['area'].id])
        elif operator in Interpreter.ALLOWED_CONNECTIONS:
            try:
                destination = self.models['area'].outgoing.get(title=command).area_to
                return reverse('explore:area', args=[destination.id])
            except ObjectDoesNotExist:
                    activity = Activity(
                        area=self.models['area'],
                        creator=self.models['user'],
                        creator_only=True,
                        activity_text=f'Connection "{command}" does not exist',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])
        else:
            # If no command, leave a message
            activity_text = f'{self.models["user"].username}: {command}'
            activity = Activity(
                creator=self.models['user'],
                area=self.models['area'],
                activity_text=activity_text)
            activity.save()
            if self.models['user'].id != self.models['area'].creator.id:
                score = self.models['area'].creator.score
                score.total += 1
                score.save()

    def validate_connection(title):
        return len(title) > 0 and title in Interpreter.ALLOWED_CONNECTIONS
