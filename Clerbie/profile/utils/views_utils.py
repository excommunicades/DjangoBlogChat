from authify.models import Clerbie

def get_user_by_request(request_user):

    try:

        user = Clerbie.objects.get(nickname=str(request_user))

    except Clerbie.DoesNotExist:

        return None

    return user