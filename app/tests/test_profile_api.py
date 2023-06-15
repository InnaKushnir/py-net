from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Profile, Post
from user.models import User

PROFILE_URL = reverse("app:profile-list")
POST_URL = reverse("app:post-list")


class UnauthenticatedProfileApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedWithoutProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin0@gmail.com",
            "12345admin0",
        )
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.create(user=self.user, username="Testusername")

    def test_list_profile_without_profile(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(any(profile['id'] == self.profile.id for profile in response.data['results']))


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin0@gmail.com",
            "12345admin0",
        )
        self.client.force_authenticate(self.user)

        self.profile = Profile.objects.create(user=self.user, username="Testusername")
        self.user1 = get_user_model().objects.create_user(
            "admin111@gmail.com",
            "12345admin11",
        )
        self.user2 = get_user_model().objects.create_user(
            "admin2@gmail.com",
            "12345admin2",
        )
        self.user3 = get_user_model().objects.create_user(
            "admin3@gmail.com",
            "12345admin3",
        )
        self.profile1 = Profile.objects.create(user=self.user1, username="Testusername1")
        self.profile2 = Profile.objects.create(user=self.user2, username="Testusername2")
        self.profile3 = Profile.objects.create(user=self.user3, username="Testusername3")
        self.post = Post.objects.create(owner=self.user, profile=self.profile, title="Test Post",
                                        content="Post Test content")
        self.post1 = Post.objects.create(owner=self.user1, profile=self.profile1, title="Test1 Post1",
                                         content="Post1 Test1 content")
        self.post2 = Post.objects.create(owner=self.user2, profile=self.profile2, title="Test2 Post2",
                                         content="Post2 Test2 content")
        self.profile.followings.add(self.profile1)
        self.profile.followings.add(self.profile2)

    def test_posts_list(self):
        response = self.client.get(POST_URL)

        posts_ids = [post["id"] for post in response.data["results"]]

        following_posts = Post.objects.filter(profile__in=self.profile.followings.all())
        following_posts_ids = following_posts.values_list("id", flat=True)


        self.profile_posts = Post.objects.filter(profile=self.profile)
        self.profile_posts_ids = self.profile_posts.values_list("id", flat=True)
        for post_id in self.profile_posts_ids:
            self.assertIn(post_id, posts_ids)

        expected_ids = list(self.profile_posts_ids) + list(following_posts_ids)
        print(expected_ids, posts_ids)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(posts_ids, [1, 2, 3])

