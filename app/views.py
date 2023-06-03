from django.db.models import Q, Count
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views import generic
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, generics, status, serializers, request, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from app.models import Post, PostLike, Profile, Comment
from app.serializers import (
    PostSerializer,
    PostLikeSerializer,
    ProfileSerializer,
    ProfileFollowAddSerializer,
    CommentSerializer,
    LikedPostsSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    ProfileNoPostSerializer, CommentCreateSerializer, ProfileCreateSerializer, ProfileSearchSerializer
)
from rest_framework.permissions import BasePermission

from pagination import PyNetListPagination


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return obj.owner == request.user


class IsUserOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return obj.user == request.user


class HasProfilePermission(BasePermission):
    message = "User has no profile. Create profile, please."

    def has_permission(self, request, view):
        user = request.user
        return hasattr(user, 'profile')


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly, HasProfilePermission)
    queryset = Post.objects.all().select_related("owner")
    pagination_class = PyNetListPagination
    """Endpoint to search post by  hashtags"""
    filter_backends = [filters.SearchFilter]
    search_fields = ['content']

    def get_queryset(self):
        user = self.request.user
        following_profiles = user.profile.following.all()
        queryset = Post.objects.filter(profile__in=following_profiles).select_related(
            "owner") | Post.objects.filter(profile=user.profile)
        if self.action == "list" and self.request.method == "retrieve":
            profile_pk = self.kwargs["profile_pk"]
            return queryset.filter(profile_id=profile_pk)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        profile_id = self.request.user.profile.id
        profile = get_object_or_404(Profile, pk=profile_id)
        user = self.request.user
        title = self.request.data.get("title")
        content = self.request.data.get("content")
        serializer.save(profile=profile, owner=user, content=content, title=title)


class PostLikeCreateView(generics.CreateAPIView):
    """Endpoint for create postlike"""
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        post = self.get_post()
        author = self.request.user
        serializer.save(author=author, post=post)

    def get_post(self):
        post_id = self.kwargs["pk"]
        post = get_object_or_404(Post, pk=post_id)
        return post

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["post"] = self.get_post()
        return context


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all().select_related("user")
    permission_classes = (IsUserOrReadOnly, HasProfilePermission)
    pagination_class = PyNetListPagination

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_permissions(self):
        if self.action == "follow":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return ProfileCreateSerializer
        if self.action == "follow":
            return ProfileFollowAddSerializer
        if self.action in ['retrieve'] and self.request.user.is_authenticated:
            profile = self.get_object()
            follower = self.request.user.profile
            if profile.followings.filter(id=follower.id).exists() or profile == follower:
                return ProfileSerializer
            return ProfileNoPostSerializer

        return ProfileSerializer

    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None):
        """Endpoint to join the profile followers"""
        profile = self.get_object()
        following = request.user.profile
        profile.followings.add(following)
        serializer = self.get_serializer(profile, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def followers_list(self, request, pk=None):
        """Endpoint to get the list of followers"""
        user = self.get_object()
        followers = user.followings.all()
        serializer = ProfileSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following_list(self, request, pk=None):
        """Endpoint to get the list of following"""
        profile = self.get_object()
        following = profile.following.all()
        serializer = ProfileSerializer(following, many=True)
        return Response(serializer.data)


class ProfileSearchView(generics.ListAPIView):
    serializer_class = ProfileSearchSerializer
    permission_classes = (IsAuthenticated, HasProfilePermission)
    lookup_field = "username"

    def get_queryset(self):
        username = self.kwargs["username"]
        return Profile.objects.filter(
            user__profile__username__icontains=username
        ).select_related("user")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                type={"type": "string"},
                description="Permissions only for user, who authenticated,"
                            " (ex. api/profile/An  return profile of user whose username consists An)",
                required=False,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        post_id = self.kwargs["pk"]
        post = get_object_or_404(Post, pk=post_id)
        user = self.request.user
        content = self.request.data.get("content")
        comment = Comment(user=user, post=post, content=content)
        comment.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().select_related("user")
    permission_classes = [IsUserOrReadOnly]
    pagination_class = PyNetListPagination

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


class LikedPostsView(generics.ListAPIView):
    serializer_class = LikedPostsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PyNetListPagination

    def get_queryset(self):
        user = self.request.user
        post_likes = PostLike.objects.filter(
            Q(author=user),
            Q(status=PostLike.StatusChoices.LIKE)
            | Q(status=PostLike.StatusChoices.UNLIKE),
        ).select_related("post")

        liked_posts = [post_like.post for post_like in post_likes]
        return liked_posts
