from engineauth import models

class CustomUser(models.User):
    @classmethod
    def _get_kind(cls):
        return 'EAUser'
