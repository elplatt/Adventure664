from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from .models import Activity

from item.models import Item

class Interpreter(object):

    ALLOWED_CONNECTIONS = [
        'north',
        'south',
        'east',
        'west',
        'up',
        'down'
    ]

    def __init__(self, models, request):
        # Save models
        self.models = models
        self.request = request

    def info(self, text):
        messages.add_message(self.request, messages.INFO, text)

    def error(self, text):
        messages.add_message(self.request, messages.ERROR, text)

    def execute(self, command):

        # Parse command into words
        operator, target = '', ''
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
                    self.error('You must specify a connection title, e.g., "north".')
                    return reverse('explore:area', args=[self.models['area'].id])
        if operator == 'delete':
            if target == 'connection':
                title = ' '.join(words[2:]).strip().lower()
                try:
                    connection = self.models['area'].outgoing.get(title__iexact=title)
                except ObjectDoesNotExist:
                    self.error(f'Connection "{title}" does not exist')
                    return reverse('explore:area', args=[self.models['area'].id])

                # Make sure user created connection
                if connection.creator is not None and connection.creator.id != self.models['user'].id:
                    self.error(f'Someone else created "{target}", you can\'t delete it... yet.')
                    return reverse('explore:area', args=[self.models['area'].id])

                # Send to the delete form
                kwargs = {
                    'source_id': self.models['area'].id,
                    'title': connection.title,
                }
                return reverse('explore:delete_connection', kwargs=kwargs)
            else:
               self.error('You can\'t delete that... yet.')
               return reverse('explore:area', args=[self.models['area'].id])
        elif operator == 'edit':
            if target == 'area':
                return reverse('explore:edit_area', args=[self.models['area'].id])
            elif target == 'description':
                self.info('Note: "edit area" is way cooler than "edit description".')
                return reverse('explore:area_description', args=[self.models['area'].id])
        elif operator == 'unpublish':
            if self.models['area'].creator == self.models['user']:
                self.models['area'].published = False
                self.models['area'].save()
                self.info('This area has been unpublished.')
            else:
                self.error('You can\'t unpublish an area created by another player... yet.')
                return reverse('explore:area', args=[self.models['area'].id])
        elif operator == 'publish':
            self.models['area'].published = True
            self.models['area'].save()
            self.info('This area has been published to the front page.')
            return reverse('explore:area', args=[self.models['area'].id])
        elif operator == 'status':
            status = ' '.join(words[1:])
            self.models['user'].player.status = status
            self.models['user'].player.save()
            self.info(f'Your status has been updated to:\n{self.models["user"].username} {status}')
        elif operator == 'look':
            look_at = ' '.join(words[1:])
            try:
                item = self.models['area'].item_set.filter(title__iexact=look_at)[0]
                self.info(item.long_description)
            except IndexError:
                self.error('You don\'t see that here.')
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
                    self.error(f'Connection "{command}" does not exist')
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
