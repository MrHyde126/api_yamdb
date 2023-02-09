from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    GetTokenView,
    ReviewViewSet,
    SendCodeView,
    TitleViewSet,
    UserCreateAdminView,
    UserMeView,
    UserPatchAdminView,
)

router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SendCodeView.as_view()),
    path('v1/auth/token/', GetTokenView.as_view()),
    path('v1/users/me/', UserMeView.as_view()),
    path('v1/users/', UserCreateAdminView.as_view()),
    path('v1/users/<str:username>/', UserPatchAdminView.as_view()),
]
