from django.core.exceptions import FieldError
from django_filters import utils
from django_filters.rest_framework import DjangoFilterBackend

from exceptions import IncorrectParametersException


class AdvancedDjangoFilterBackend(DjangoFilterBackend):

    excluded_filter_keywords = ['limit', 'offset', 'ordering']

    @staticmethod
    def build_filters(params):
        filters = []
        for key, value in params.items():
            if key not in AdvancedDjangoFilterBackend.excluded_filter_keywords and value is not None and \
                    value != '':
                query_filter = {key: value}
                filters.append(query_filter)
        return filters

    def filter_queryset(self, request, queryset, view):
        filter_set = self.get_filterset(request, queryset, view)
        if filter_set is None:
            return queryset

        if not filter_set.is_valid() and self.raise_exception:
            raise utils.translate_validation(filter_set.errors)

        try:
            filters = self.build_filters(request.GET)
            for query_filter in filters:
                queryset = queryset.filter(**query_filter).distinct()
        except FieldError as e:
            raise IncorrectParametersException().details(e)

        return queryset
