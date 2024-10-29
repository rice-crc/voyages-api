from flask_login import UserMixin


DJANGO_BASE_URL="http://voyages-api:8000/"
DJANGO_AUTH_KEY="Token ....."
FLASK_SECRET_KEY="........."


class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

USERS = {
    1: User(".....", 1)
}
USER_NAMES = dict((u.name, u) for u in USERS.values())

PW="........."

# DEBUG=True

TMP_PATH="/mnt/geo_networks_tmp"

rebuilder_number_of_workers=1