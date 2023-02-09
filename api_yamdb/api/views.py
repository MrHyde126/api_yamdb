from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminModeratorOwnerOrReadOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SendCodeSerializer,
    TitlePostPatchSerializer,
    TitleSerializer,
    UserEditMeSerializer,
    UserMeSerializer,
    send_mail_token,
)
from reviews.models import Category, Genre, Review, Title, User


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email'),
        ).last()
        if user:
            send_mail_token(user)
            return Response(request.data, status=status.HTTP_200_OK)
        serializer = SendCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if not serializer.is_valid():
            raise serializers.ValidationError('Неверные данные')
        user = get_object_or_404(User, username=serializer.data['username'])

        if default_token_generator.check_token(
            user, serializer.data['confirmation_code']
        ):
            access_token = AccessToken.for_user(user)
            return Response(
                {'token': str(access_token)}, status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный проверочный код'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserMeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserEditMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserEditMeSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateAdminView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserMeSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'


class UserPatchAdminView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserMeSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs['username'])

    def put(self, request, *args, **kwargs):
        serializer = UserMeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


class GenreViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(
            request.data, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update(self, request, *args, **kwargs):
        return Response(
            request.data, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_serializer_context(self, *args, **kwargs):
        try:
            if self.kwargs['slug']:
                raise MethodNotAllowed(method='GET')
        except KeyError:
            pass


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return TitlePostPatchSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAdminModeratorOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )
    serializer_class = CommentSerializer

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'),
        )
        review = get_object_or_404(
            Review, title=title, pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'),
        )
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title,
        )
        serializer.save(
            author=self.request.user,
            review=review,
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'),
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'),
        )
        serializer.save(
            author=self.request.user,
            title=title,
        )
