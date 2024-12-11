from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import AnonymousUser

from api.api_actions.serializers.posts_serializers import (
    PostsOutSerializer,
    PostsInSerializer,
    PostsUpdateSerializer,
    SetReactionSerializer
)
from api.api_actions.utils.posts_utils import (
    update_post,
    delete_post,
    post_paginator
)

from publish.models import Posts, PostReactions

class PostListCreate(generics.ListCreateAPIView):



    def get_serializer_class(self):

        if self.request.method == 'GET':

            return PostsOutSerializer

        return PostsInSerializer

    def get_queryset(self):

            page = self.request.query_params.get('page', None)

            if page and not page.isdigit():

                raise ValidationError({"error": "Query parameter does not exist."})

            page_size = 3

            return post_paginator(page=page, page_size=page_size)

    def get(self, request, *args, **kwargs):

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

        if not request.user.is_authenticated:

            return Response({"errors": {"error": "You need to authenticate for this action."}}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            serializer.save()

            return Response({"message": "Post created successfully."})

        formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)

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

            return Response({"error": "Post not found."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):

        if not request.user.is_authenticated:

            return Response({"errors": {"error": "You need to authenticate for this action."}}, status=status.HTTP_401_UNAUTHORIZED)

        object = self.get_object()

        return update_post(self, request, object)

    def patch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:

            return Response({"errors": {"error": "You need to authenticate for this action."}}, status=status.HTTP_401_UNAUTHORIZED)

        object = self.get_object()

        return update_post(self, request, object)

    def delete(self, request, *args, **kwargs):

        if not request.user.is_authenticated:

            return Response({"errors": {"error": "You need to authenticate for this action."}}, status=status.HTTP_401_UNAUTHORIZED)

        object = self.get_object()

        return delete_post(self, request, object)


class SetReactionToPOST(generics.GenericAPIView):

    authentication_classes = [JWTAuthentication]

    serializer_class = SetReactionSerializer

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:

            return Response({"errors": {"error": "You need to authenticate for this action."}}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)

        user = request.user

        if user:

            if serializer.is_valid():

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
