from http.client import BAD_REQUEST, OK

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .mixins import CreateListViewSet
from .permissions import (IsAdminOrIsSuperUser, IsAdminOrIsSuperUserOrReadOnly,
                          IsAdminOrModeratorOrAuthorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleGETSerializer, TitleSerializer, TokenSerializer,
                          UserSerializer)


class SignUpUser(APIView):
    """APIView для регистрации пользователей."""

    serializer_class = SignUpSerializer
    permission_classes = ([permissions.AllowAny])

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(
            username=serializer.validated_data.get('username'),
            email=serializer.validated_data.get('email'))
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Token: {confirmation_code}',
            from_email=None,
            recipient_list=(user.email,),
            fail_silently=False
        )
        return Response(serializer.data, status=OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Функция для получения токена."""

    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"Token": str(token)}, status=OK)

    return Response(serializer.errors, status=BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrIsSuperUser]
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False,
            methods=["GET", "PATCH"],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=User.USER)
        return Response(serializer.data, status=OK)


class CategoryViewSet(CreateListViewSet):
    """Вьюсет для создания объектов Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(CreateListViewSet):
    """Вьюсет для создания объектов Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Title."""

    queryset = Title.objects.annotate(rating=Avg('titles__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrIsSuperUserOrReadOnly]
    pagination_class = LimitOffsetPagination
    search_fields = ("category__slug", "genre__slug", "name", "year")
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Выбор сериализатора для разных типов запроса."""
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Review."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrModeratorOrAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Comment."""

    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrModeratorOrAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())
