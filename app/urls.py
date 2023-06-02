from IPython.core.profileapp import ProfileCreate
from django.urls import include, path
from rest_framework import routers
from app.views import (
    PostViewSet,
    PostLikeCreateView,
    ProfileViewSet,
    ProfileSearchView,
    CommentCreateView,
    LikedPostsView,
    CommentViewSet,
)

router = routers.DefaultRouter()
router.register("profile", ProfileViewSet)
router.register("post", PostViewSet)
router.register("comment", CommentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "profile/search/<str:username>/",
        ProfileSearchView.as_view(),
        name="profile-search",
    ),
    path(
        "post/<int:pk>/postlike/create/",
        PostLikeCreateView.as_view(),
        name="postlike-create",
    ),
    path(
        "post/<int:pk>/comment/create/",
        CommentCreateView.as_view(),
        name="comment-create",
    ),
    path("posts/liked/", LikedPostsView.as_view(), name="liked-posts"),
    path(
        "profile/<int:profile_pk>/follow/",
        ProfileViewSet.as_view({"post": "follow"}),
        name="profile-follow",
    ),
    path(
        "profile/<int:pk>/followers/",
        ProfileViewSet.as_view({"get": "followers_list"}),
        name="profile-followers"
    ),
    path(
        "profile/<int:pk>/following/",
        ProfileViewSet.as_view({"get": "following_list"}),
        name="profile-following"
    ),
]

app_name = "app"
