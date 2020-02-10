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

        # Get connections for current area
        connection_titles = [c.title.lower().strip() for c in self.models['area'].outgoing.all()]

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
                        activity_text='You must specify a connection title, e.g., "north".',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])
        if operator == 'delete':
            if target == 'connection':
                title = ' '.join(words[2:]).strip().lower()
                try:
                    connection = self.models['area'].outgoing.get(title__iexact=title)
                except ObjectDoesNotExist:
                    activity = Activity(
                        area=self.models['area'],
                        creator=self.models['user'],
                        creator_only=True,
                        activity_text=f'Connection "{title}" does not exist',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])

                # Make sure user created connection
                if connection.creator is not None and connection.creator.id != self.models['user'].id:
                    activity = Activity(
                        area=self.models['area'],
                        creator=self.models['user'],
                        creator_only=True,
                        activity_text=f'Someone else created "{target}", you can\'t delete it... yet',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])

                # Send to the delete form
                kwargs = {
                    'source_id': self.models['area'].id,
                    'title': connection.title,
                }
                return reverse('explore:delete_connection', kwargs=kwargs)
        elif operator == 'edit':
            if target == 'description':
                return reverse('explore:area_description', args=[self.models['area'].id])
        elif command in connection_titles:
            try:
                connection = self.models['area'].outgoing.get(title__iexact=command)
                destination = connection.area_to
                if connection.creator is not None and connection.creator.id != self.models['user'].id:
                    # Update score
                    score = connection.creator.score
                    score.total += 1
                    score.save()
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
        return len(title) > 0 
