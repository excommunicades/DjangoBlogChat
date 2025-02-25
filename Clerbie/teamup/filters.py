from django_filters import rest_framework as filters

from django.db.models import Q

from teamup.models import Announcement


class AnnouncementFilter(filters.FilterSet):

    job_title = filters.CharFilter(method='filter_job_title')
    title = filters.CharFilter(method='filter_title')
    technologies = filters.CharFilter(method='filter_technologies')

    class Meta:
        model = Announcement
        fields = ['job_title', 'title', 'technologies']

    def filter_job_title(self, queryset, name, value):

        job_titles_keywords = value.split('-')
        
        q_objects = Q()
        for keyword in job_titles_keywords:
            q_objects &= Q(job_titles__title__icontains=keyword)
        
        queryset = queryset.filter(q_objects).distinct()

        return queryset

    def filter_title(self, queryset, name, value):

        title_keywords = value.split('-')
        
        q_objects = Q()
        for keyword in title_keywords:
            q_objects &= Q(title__icontains=keyword)

        return queryset.filter(q_objects).distinct()

    def filter_technologies(self, queryset, name, value):

        tech_list = value.split('-')
        queryset = queryset.prefetch_related('technologies')
        
        for tech in tech_list:
            queryset = queryset.filter(technologies__name__icontains=tech)

        return queryset.distinct()
