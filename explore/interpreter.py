from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from .models import Activity, Area, Connection

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

    def current_url(self):
        return self.request.path
    
    def error_url(self):
        return self.request.path

    def info(self, text):
        messages.add_message(self.request, messages.INFO, text)

    def error(self, text):
        messages.add_message(self.request, messages.ERROR, text)

    def execute(self, raw_command):

        # Parse command into words
        operator, target = '', ''
        command = raw_command.strip().lower()
        words = command.split(' ')
        raw_words = raw_command.split(' ')
        if len(words) > 0:
            operator = words[0].strip().lower()
        if len(words) > 1:
            target = words[1].strip().lower()

        # Get connections for current area
        connection_titles = [c.title.lower().strip() for c in self.models['area'].outgoing.all()]

        # Determine type of command
        if operator == 'help':
            # Send to How To Play page
            return reverse('guide')
        if operator == 'create':
            if target == 'area':
                title = ' '.join(raw_words[2:]).strip()
                try:
                    Area.objects.get(title__iexact=title.lower())
                    self.error(f'Area "{title}" already exists.')
                    return self.current_url()
                except ObjectDoesNotExist:
                    pass
                if title:
                    url = reverse('explore:create_area', args=[title])
                else:
                    url = reverse('explore:create_area')
                return url
            elif target == 'connection':
                title = ' '.join(words[2:]).strip().lower()
                if Interpreter.validate_connection(title):
                    Connection(
                        title=title,
                        area_from=self.models['area'],
                        creator=self.request.user
                        ).save()
                    if self.models['area'].creator != request.user:
                        # Update score
                        score = self.models['area'].creator.score
                        score.total += 5
                        score.save()
                        self.models['area'].creator.score = score
                    messages.add_message(
                        self.request,
                        messages.INFO,
                        'Created connection "{}"'.format(title))
                    return self.current_url()
                else:
                    self.error('You must specify a connection title, e.g., "north".')
                    return self.error_url()
            elif target == 'item':
                url = '{}?next={}'.format(
                    reverse('item:create', args=[self.models['area'].id]),
                    self.current_url())
                return url
        if operator == 'delete':
            if target == 'connection':
                title = ' '.join(words[2:]).strip().lower()
                try:
                    connection = self.models['area'].outgoing.get(title__iexact=title)
                except ObjectDoesNotExist:
                    self.error(f'Connection "{title}" does not exist')
                    return self.error_url()

                # Make sure user created connection
                if (connection.creator is not None
                        and connection.creator != self.models['user']
                        and connection.area_from.creator != self.models['user']):
                    self.error(f'Someone else created "{title}", you can\'t delete it... yet.')
                    return self.error_url()

                # Send to the delete form
                kwargs = {
                    'source_id': self.models['area'].id,
                    'title': connection.title,
                }
                url = '{}?next={}'.format(
                    reverse('explore:delete_connection', kwargs=kwargs),
                    self.current_url())
                return url
            elif target == 'item':
                title = ' '.join(words[2:]).strip().lower()
                try:
                    item = self.models['area'].item_set.get(title__iexact=title)
                except ObjectDoesNotExist:
                    self.error(f'Item "{title}" does not exist')
                    return self.error_url()

                # Make sure user created item
                if item.creator and item.creator != self.models['user']:
                    self.error(f'Someone else created "{title}", you can\'t delete it... yet.')
                    return self.error_url()

                # Send to the delete form
                kwargs = {
                    'item_id': item.id,
                }
                url = '{}?next={}'.format(
                    reverse('item:delete', kwargs=kwargs),
                    self.current_url())
                return url
            else:
               self.error('You can\'t delete that... yet.')
               return self.error_url()
        elif operator == 'edit':
            if target == 'area':
                url = '{}?next={}'.format(
                    reverse('explore:edit_area', args=[self.models['area'].id]),
                    self.current_url())
                return url
            elif target == 'description':
                self.info('Note: "edit area" is way cooler than "edit description".')
                url = '{}?next={}'.format(
                    reverse('explore:area_description', args=[self.models['area'].id]),
                    self.current_url())
                return url
        elif operator == 'warp':
            title = ' '.join(words[1:]).strip()
            if not title:
                self.error('Warp where?')
                return self.error_url()
            try:
                area = Area.objects.get(title__iexact=title)
            except ObjectDoesNotExist:
                self.error(f'There is no area named "{title}".')
                return self.error_url()
            # Update score
            if area.creator and area.creator != self.models['user']:
                score = area.creator.score
                score.total += 3
                score.save()
            return reverse('explore:area', args=[area.id])
        elif operator == 'unpublish':
            if self.models['area'].creator == self.models['user']:
                self.models['area'].published = False
                self.models['area'].save()
                self.info('This area has been unpublished.')
            else:
                self.error('You can\'t unpublish an area created by another player... yet.')
                return self.error_url()
        elif operator == 'publish':
            self.models['area'].published = True
            self.models['area'].save()
            self.info('This area has been published to the front page.')
        elif operator == 'status':
            if not self.models['user'].is_authenticated:
                self.error('Only logged in users can set a status.')
                return self.error_url()
            status = ' '.join(words[1:])
            self.models['user'].player.status = status
            self.models['user'].player.save()
            self.info(f'Your status has been updated to:\n{self.models["user"].username} {status}')
        elif operator == 'look':
            look_at = ' '.join(words[1:])
            try:
                item = self.models['area'].item_set.filter(title__iexact=look_at)[0]
                self.info(item.long_description)
                # Update scores
                if self.models['user'] != item.creator:
                    score = item.creator.score
                    score.total += 1
                    score.save()
            except IndexError:
                self.error('You don\'t see that here.')
                return self.error_url()
        elif operator == 'exit' or operator == 'logout':
            self.info('You have been logged out.')
            return '{}?next={}'.format(reverse('logout'), reverse('explore:index'))
        elif command in connection_titles:
            try:
                connection = self.models['area'].outgoing.get(title__iexact=command)
                destination = connection.area_to
                if connection.creator != self.models['user']:
                    # Update score
                    score = connection.creator.score
                    score.total += 1
                    score.save()
                if connection.area_to == None:
                    # Connection to nowhere, go to create form
                    url = '{}?next={}'.format(
                        reverse('explore:edit_connection', args=[connection.area_from.id, connection.title]),
                        self.current_url())
                    return url
                return reverse('explore:area', args=[destination.id])
            except ObjectDoesNotExist:
                    self.error(f'Connection "{command}" does not exist')
                    return self.error_url()
        else:
            # If no command, leave a message
            if not self.models['user'].is_authenticated:
                self.error('That command is only available to registered users, please login.')
                return self.error_url()
            activity_text = f'{self.models["user"].username}: {raw_command}'
            activity = Activity(
                creator=self.models['user'],
                area=self.models['area'],
                activity_text=activity_text)
            activity.save()
            if self.models['area'].creator and self.models['user'] != self.models['area'].creator:
                score = self.models['area'].creator.score
                score.total += 1
                score.save()
                
        # If no other url given, use current url
        return self.current_url()

    def validate_connection(title):
        return len(title) > 0 
