from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Profile

PROFILE_URL = reverse("app:profile-list")


class UnauthenticatedProfileApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedWithoutProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin0@gmail.com",
            "12345admin0",
        )
        self.client.force_authenticate(self.user)

    def test_list_profile_without_profile(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('User has no profile. Create profile, please.', response.data['detail'])


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

    def test_list_profile_with_profile(self):
        self.client.force_authenticate(self.profile.user)
        response = self.client.get(PROFILE_URL)
        profile_ids = [profile["id"] for profile in response.data["results"]]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_ids, [self.profile.id, self.profile1.id, self.profile2.id, self.profile3.id])

    def test_list_followers(self):
        self.profile.followings.add(self.profile1)
        self.profile.followings.add(self.profile2)

        response = self.client.get(reverse("app:profile-followers", kwargs={'pk': self.profile.id}))
        profile_ids = [profile["id"] for profile in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_ids, [self.profile1.id, self.profile2.id])

    def test_list_followings(self):
        self.profile.followings.add(self.profile1)
        response = self.client.get(reverse("app:profile-following", kwargs={'pk': self.profile1.id}))
        profile_ids = [profile["id"] for profile in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_ids, [self.profile.id])

    def test_profile_follow(self):
        response = self.client.post(reverse("app:profile-follow", kwargs={'pk': self.profile3.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile_id"], self.profile3.id)

    def test_profile_search(self):
        response = self.client.get(reverse("app:profile-search", kwargs={"username": "name1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["username"], "Testusername1")
