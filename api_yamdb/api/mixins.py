from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAdminOrReadOnly


class CreateListViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов"""

    filter_backends = (filters.SearchFilter,)
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    search_fields = ('name',)
    lookup_field = 'slug'
