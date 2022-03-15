from moderation import moderation
from moderation.moderator import GenericModerator
from voyage.models import Voyage



moderation.register(Voyage)
