from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (IsAdministrator, IsAdministratorOrReadOnly,
                          IsAuthorOrStaffOrReadOnly)
from .serializers import (CategorySerializer, CodeSerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SignUpSerializer, TitlePostSerializer,
                          TitleViewSerializer, UserInfoSerializer,
                          UserSerializer)


class SignUp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            user = User.objects.create(
                username=username,
                email=email
            )
            token = default_token_generator.make_token(user)
            subject = 'Спасибо за регистрацию в нашем чудо сервисе'
            send_mail(
                subject=subject,
                message=f'Ваш токен авторизации: {token}',
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[email]
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.data.get('username')
            )
            confirmation_code = serializer.data.get('confirmation_code')
            if default_token_generator.check_token(user, confirmation_code):
                token = AccessToken.for_user(user)
                return Response(
                    {'Ваш токен доступа к API': str(token)},
                    status=status.HTTP_200_OK
                )
            return Response(
                'Неверный код доступа',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdministrator,)
    filterset_fields = ['username']
    lookup_field = 'username'

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserInfoSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data,
                            status=status.HTTP_200_OK
                            )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg("reviews__score")).order_by('name')
    permission_classes = (IsAdministratorOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleViewSerializer
        return TitlePostSerializer


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdministratorOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdministratorOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('author', 'text', 'title',)
    search_fields = ('author', 'text', 'title',)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly, )
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('author', 'text', 'review', )
    search_fields = ('author', 'text', 'review', )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title__id=self.kwargs.get('title_id'),
            pk=self.kwargs.get('review_id')
        )
        return review.comment.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title__id=self.kwargs.get('title_id'),
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
