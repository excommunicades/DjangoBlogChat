from rest_framework.response import Response
from rest_framework import status

from publish.models import Posts

def update_post(self, request, object):

    serializer = self.get_serializer(object, data=request.data)

    if serializer.is_valid():

        user = request.user

        request_user = user.nickname

        post = object.title

        post = Posts.objects.filter(owner=object.owner, title=post)

        if str(request_user) == str(post[0].owner) or str(user.role) == 'admin':

            serializer.save()

            return Response({"message": "Post updated successfully."})

        return Response({"message": "You are not the owner of this post"})

    formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

    return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)


def delete_post(self, request, object):

    object = self.get_object()

    if object:

        user = request.user

        request_user = user.nickname

        post = object.title

        post = Posts.objects.filter(owner=object.owner, title=post)

        if str(request_user) == str(post[0].owner) or str(user.role) == 'admin':

            post.delete()

            return Response({"message": "Post deleted successfully."})

        return Response({"message": "You are not a owner of this post"})

    formatted_errors = {field: error[0] for field, error in serializer.errors.items()}

    return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)


def post_paginator(page, page_size):

    if page:

        page_number = int(page)

        if page_number > 1:

            start = (page_number-1) * page_size

            end = start + page_size

            queryset = Posts.objects.all()[start:end]

        else:

            start = 0

            end = page_size

            queryset = Posts.objects.all()[start:end]

    else:

        queryset = Posts.objects.all()[0:page_size]

    return queryset
