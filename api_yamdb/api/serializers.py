from django.db.models import Q
from rest_framework import serializers, validators
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
    )

    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в имени пользователя')
        check_email = User.objects.filter(
            email=data.get('email').lower()
        ).exists()
        check_username = User.objects.filter(
            username=data.get('username').lower()
        ).exists()
        check_user = User.objects.filter(
            Q(email=data.get('email').lower())
            & Q(username=data.get('username').lower())
        ).exists()
        if check_user:
            return data
        if check_username:
            raise serializers.ValidationError(
                'Неверный адрес электронной почты'
            )
        if check_email:
            raise serializers.ValidationError(
                'Адрес электронной почты занят'
            )
        return data

    class Meta:
        fields = ('username', 'email')
        model = User


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        exclude = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre"""

    class Meta:
        model = Genre
        exclude = ("id",)


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title

    def to_representation(self, title):
        """Определяет какой сериализатор будет использоваться для чтения."""
        return TitleGETSerializer(title).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                    author=self.context['request'].user).exists():
                raise validators.ValidationError(
                    'Нельзя оставлять более одного отзыва на произведение.')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
