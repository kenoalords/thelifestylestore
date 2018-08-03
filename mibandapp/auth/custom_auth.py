from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class CustomEmailAuthBackend:

    def authenticate(self, request, username=None, password=None):
        # Check tracking cookie and if None, return None
        try:
            user_cookie = request.get_signed_cookie('_t')
        except Exception as ex:
            return None

        try:

            user = User.objects.get(email=username)
            pass_valid = check_password(password, user.password)
            if user and pass_valid and user_cookie:
                return user
            else:
                return None
        except Exception as ex:
            print('User does not exist')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
