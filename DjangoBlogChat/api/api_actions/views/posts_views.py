from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.api_actions.serializers.posts_serializers import (
    PostsOutSerializer,
    PostsInSerializer,
    PostsUpdateSerializer,
    SetReactionSerializer
)
from api.api_actions.utils.posts_utils import (
    update_post,
    delete_post
)

from publish.models.posts_models import Posts, PostReactions


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

                print(serializer.data)

                reactions = PostReactions.objects.filter(post=serializer.data.get('pk'))

                like = 0
                dislike = 0

                for post in reactions:

                    match post.reaction:
                        case 'like':
                            like += 1
                        case 'dislike':
                            dislike += 1

                response_data = serializer.data

                response_data['like'] = like
                response_data['dislike'] = dislike

                return Response(response_data, status=status.HTTP_200_OK)

            except Posts.DoesNotExist:

                return Response({"error": "Post not found."}, status=status.HTTP_400_BAD_REQUEST)

        else:

            posts = self.get_queryset()

            response_data = []

            for post in posts:

                serializer = self.get_serializer(post)

                reactions = PostReactions.objects.filter(post=post)

                like_counter = 0
                dislike_counter = 0

                for reaction in reactions:
                    if reaction.reaction == 'like':
                        like_counter += 1
                    elif reaction.reaction == 'dislike':
                        dislike_counter += 1

                post_data = serializer.data
                post_data['like'] = like_counter
                post_data['dislike'] = dislike_counter

                response_data.append(post_data)

            return Response(response_data, status=status.HTTP_200_OK)

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


class SetReactionToPOST(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = SetReactionSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        user = request.user

        if user:

            if serializer.is_valid():
                print(serializer.validated_data.get('post').pk)

                try:

                    post_reaction = PostReactions.objects.get(post=serializer.validated_data.get('post').pk)

                except:

                    post_reaction = None

                if post_reaction:

                    if user == post_reaction.user:

                        if post_reaction:

                            if post_reaction.reaction == serializer.validated_data.get('reaction'):

                                post_reaction.delete()
                                print('deleted')

                                return Response({"message": "reaction was successfully removed"}, status=status.HTTP_200_OK)

                            else:

                                post_reaction.reaction = serializer.validated_data.get('reaction')

                                post_reaction.save()
                                print('updated')
                                return Response({"message": "reaction was successfully changed"}, status=status.HTTP_200_OK)
                else:

                    serializer.save(user=user)
                    print('created')

                return Response({"message": "reaction was successfully set"}, status=status.HTTP_200_OK)

            errors = serializer.errors

            formatted_errors = {field: error[0] for field, error in errors.items()}

            return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"errors": {"error": "User does not found."}})
