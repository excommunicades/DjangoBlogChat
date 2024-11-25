from blog_user.models import BlogUser

def get_user_by_request(request_user):

    try:

        user = BlogUser.objects.get(nickname=str(request_user))

    except BlogUser.DoesNotExist:

        return None

    return user