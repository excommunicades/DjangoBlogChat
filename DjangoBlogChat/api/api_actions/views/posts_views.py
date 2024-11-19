from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.api_actions.serializers.posts_serializers import (
    PostsOutSerializer,
    PostsInSerializer,
    PostsUpdateSerializer
)
from api.api_actions.utils.posts_utils import (
    update_post,
    delete_post
)

from publish.models.posts_models import Posts


class PostsCRUD(generics.GenericAPIView):

    """Endpoint for posts crud-operations"""

    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):

        if self.request.method == 'GET':

            return PostsOutSerializer

        elif self.request.method == 'PUT' or self.request.method == 'PATCH':

            return PostsUpdateSerializer

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

        return delete_post(self, request, object)
