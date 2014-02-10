from django.contrib.auth import backends
from models import User

class ModelBackend(backends.ModelBackend):
    """
    Extending to provide a proxy for user
    """
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
