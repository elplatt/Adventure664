from datetime import datetime, timedelta, timezone

from django import template

register = template.Library()

@register.simple_tag
def player_status(player):
    idle = datetime.now(timezone.utc) - player.last_active
    if idle > timedelta(days=1):
        return 'was here.'
    elif idle > timedelta(hours=1):
        return 'is snoozing in the corner.'
    else:
        return 'is here.'
