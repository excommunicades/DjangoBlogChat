from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.api_actions.serializers.posts_serializers import (
    PostsOutSerializer,
    PostsInSerializer
)
from api.api_actions.utils.posts_utils import (
    update_post
)

from publish.models.models import Posts


class PostsCRUD(generics.GenericAPIView):

    """Endpoint for posts crud-operations"""

    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):

        if self.request.method == 'GET':

            return PostsOutSerializer

        return PostsInSerializer

    queryset = Posts.objects.all()


    def get(self, request, *args, **kwargs):

        if self.kwargs.get('pk'):

            try:

                object = self.get_object()

                serializer = self.get_serializer(object)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except Posts.DoesNotExist:

                return Response({"error": "Post not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:

            data = self.get_queryset()

            serializer = self.get_serializer(data, many=True)

            return Response(serializer.data)

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response({"message": "Post created successfully."})

        formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):

        object = self.get_object()

        return update_post(self, request, object)

    def patch(self, request, *args, **kwargs):

        object = self.get_object()

        return update_post(self, request, object)

    def delete(self, request, *args, **kwargs):

        object = self.get_object()

        if object:

            user = request.user

            request_user = user.nickname

            post = object.title

            post = Posts.objects.filter(owner=object.owner, title=post)

            if str(request_user) == str(post[0].owner):

                post.delete()

                return Response({"message": "Post deleted successfully."})

            return Response({"message": "You are not a owner of this post"})

        formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)
