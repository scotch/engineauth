from engineauth import models

class CustomUser(models.User):
    @classmethod
    def _get_kind(cls):
        # Override the datastore entity name.
        # The string that is returned here will be used to name the entity
        # group in the datastore
        return 'EAUser'
