from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import datetime as dt

from reviews.models import Category, Comment, Genre, Review, Title, User


class EmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)


class CodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'confirmation_code'
        ]


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'role',
            'email',
            'first_name',
            'last_name',
            'bio'
        ]

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                f'Регистрация с именем пользователя {value} запрещена!'
            )
        return value


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'role',
            'email',
            'first_name',
            'last_name',
            'bio'
        ]
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                f'Регистрация с именем пользователя {value} запрещена!'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=None)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('author', 'title',)

    def validate_rating(self, value):
        if value < 0 and value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 10'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        title_id = request.parser_context['kwargs']['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if (request.method == 'POST' and title.reviews.filter(
                author=request.user).exists()):
            raise ValidationError('не более одного отзыва')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    review = serializers.HiddenField(default=None)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'review',)


class TitleViewSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField()

    class Meta:
        fields = '__all__'
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True,
                                         slug_field='slug',
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise ValidationError(
                'В базе должны быть только уже вышедшие произведения'
            )
        return value

    class Meta:
        fields = '__all__'
        model = Title
