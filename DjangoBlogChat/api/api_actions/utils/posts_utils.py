from rest_framework.response import Response
from rest_framework import status

from publish.models.models import Posts

def update_post(self, request, object):

        serializer = self.get_serializer(object, data=request.data)

        if serializer.is_valid():

            user = request.user

            request_user = user.nickname

            post = object.title

            post = Posts.objects.filter(owner=object.owner, title=post)

            if str(request_user) == str(post[0].owner):

                serializer.save()

                return Response({"message": "Post updated successfully."})

            return Response({"message": "You are not the owner of this post"})

        formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)