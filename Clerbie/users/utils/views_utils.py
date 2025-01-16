from authify.models import Clerbie


def user_pagination(page, page_size):

    if page:

        page_number = int(page)

        if page_number > 1:

            start = (page_number - 1) * page_size

            end = start + page_size

            queryset = Clerbie.objects.all()[start:end]

        else:

            queryset = Clerbie.objects.all()[0:page_size]
    else:

        queryset = Clerbie.objects.all()[0:page_size]

    return queryset
