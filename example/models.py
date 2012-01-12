from engineauth.models import User

class EAUser(User):

    @classmethod
    def _get_kind(cls):
        return 'EAUser'
