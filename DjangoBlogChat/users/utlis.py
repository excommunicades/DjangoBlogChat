from blog_user.models import BlogUser


def user_pagination(page, page_size):

    if page:

        page_number = int(page)

        if page_number > 1:

            start = (page_number - 1) * page_size

            end = start + page_size

            queryset = BlogUser.objects.all()[start:end]

        else:

            queryset = BlogUser.objects.all()[page_number:page_size]
    else:

        queryset = BlogUser.objects.all()[0:page_size]

    return queryset
