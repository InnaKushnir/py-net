import warnings

from django.contrib.auth import get_user_model
from django.core.paginator import UnorderedObjectListWarning
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Profile, Post, Comment, PostLike
from user.models import User

PROFILE_URL = reverse("app:profile-list")
POST_URL = reverse("app:post-list")
COMMENT_URL = reverse("app:comment-list")


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
        self.assertIn("results", response.data)
        self.assertTrue(
            any(
                profile["id"] == self.profile.id for profile in response.data["results"]
            )
        )


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
        self.profile1 = Profile.objects.create(
            user=self.user1, username="Testusername1"
        )
        self.profile2 = Profile.objects.create(
            user=self.user2, username="Testusername2"
        )
        self.profile3 = Profile.objects.create(
            user=self.user3, username="Testusername3"
        )
        self.post = Post.objects.create(
            owner=self.user,
            profile=self.profile,
            title="Test Post",
            content="Post Test content",
        )
        self.post1 = Post.objects.create(
            owner=self.user1,
            profile=self.profile1,
            title="Test1 Post1",
            content="Post1 Test1 content",
        )
        self.post2 = Post.objects.create(
            owner=self.user2,
            profile=self.profile2,
            title="Test2 Post2",
            content="Post2 Test2 content",
        )
        self.post3 = Post.objects.create(
            owner=self.user3,
            profile=self.profile3,
            title="Test3 Post3",
            content="Post3 Test3 content",
        )
        self.comment = Comment.objects.create(
            post=self.post, user=self.user1, content="Test comment"
        )
        self.comment1 = Comment.objects.create(
            post=self.post, user=self.user2, content="Test2 comment"
        )
        self.postlike1 = PostLike.objects.create(
            post=self.post, status="UNLIKE", author=self.user1
        )
        self.postlike2 = PostLike.objects.create(
            post=self.post, status="LIKE", author=self.user2
        )
        self.postlike3 = PostLike.objects.create(
            post=self.post1, status="UNLIKE", author=self.user1
        )
        self.postlike4 = PostLike.objects.create(
            post=self.post1, status="LIKE", author=self.user2
        )
        self.profile.following.add(self.profile1)
        self.profile.following.add(self.profile2)
        self.profile.followings.add(self.profile1)
        self.profile.followings.add(self.profile2)

    def test_list_profile_with_profile(self):
        self.client.force_authenticate(self.profile.user)
        response = self.client.get(PROFILE_URL)
        profile_ids = [profile["id"] for profile in response.data["results"]]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(profile_ids),
            len(
                [
                    User.objects.latest("id").id,
                    self.profile.id,
                    self.profile1.id,
                    self.profile2.id,
                    self.profile3.id,
                ]
            ),
        )

    def test_list_followers(self):
        response = self.client.get(
            reverse("app:profile-followers", kwargs={"pk": self.profile.id})
        )
        profile_ids = [profile["id"] for profile in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_ids, [self.profile1.id, self.profile2.id])

    def test_list_followings(self):
        self.profile.followings.add(self.profile1)
        response = self.client.get(
            reverse("app:profile-following", kwargs={"pk": self.profile1.id})
        )
        profile_ids = [profile["id"] for profile in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_ids, [self.profile.id])

    def test_profile_follow(self):
        response = self.client.post(
            reverse("app:profile-follow", kwargs={"pk": self.profile3.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile_id"], self.profile3.id)

    def test_profile_search(self):
        response = self.client.get(
            reverse("app:profile-search", kwargs={"username": "name1"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["username"], "Testusername1")

    def test_posts_list(self):
        self.profile.following.add(self.profile1)
        self.profile.following.add(self.profile2)
        response = self.client.get(POST_URL)

        posts_ids = [post["id"] for post in response.data["results"]]

        following_posts = Post.objects.filter(profile__in=self.profile.followings.all())
        following_posts_ids = following_posts.values_list("id", flat=True)
        self.profile_posts = Post.objects.filter(profile=self.profile)
        self.profile_posts_ids = self.profile_posts.values_list("id", flat=True)
        for post_id in self.profile_posts_ids:
            self.assertIn(post_id, posts_ids)

        expected_ids = list(self.profile_posts_ids) + list(following_posts_ids)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(posts_ids, expected_ids)

    def test_posts_list_admin(self):
        self.user.is_staff = True
        response = self.client.get(POST_URL)
        posts_ids = [post["id"] for post in response.data["results"]]
        posts = Post.objects.all().values_list("id", flat=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(posts_ids, posts)

    def test_create_post(self):
        data = {
            "owner": self.user.id,
            "profile": self.profile.id,
            "title": "Test4 Post",
            "content": "Post4 Test content",
        }
        response = self.client.post(POST_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_post = Post.objects.get(id=response.data["id"])

        self.assertEqual(created_post.owner_id, self.user.id)
        self.assertEqual(created_post.profile_id, self.profile.id)
        self.assertEqual(created_post.title, "Test4 Post")
        self.assertEqual(created_post.content, "Post4 Test content")

    def test_delete_post(self):
        post_id = self.post.id
        response = self.client.delete(f"/api/post/{post_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        post_id1 = self.post1.id
        response = self.client.delete(f"/api/post/{post_id1}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post(self):
        post_id = self.post.id
        updated_data = {"title": "Updated Post", "content": "Updated content"}
        response = self.client.patch(f"/api/post/{post_id}/", data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, updated_data["title"])
        self.assertEqual(self.post.content, updated_data["content"])

        post_id1 = self.post1.id

        response = self.client.patch(f"/api/post/{post_id1}/", data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment(self):
        post_id = self.post.id
        data = {"content": "Test comment"}
        response = self.client.post(f"/api/post/{post_id}/comment/create/", data=data)
        created_comment = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_comment["content"], "Test comment")

    def test_update_comment(self):
        self.client.force_authenticate(self.user1)
        comment_id = self.comment.id
        updated_data = {"user": self.user1, "content": "Updated comment"}
        response = self.client.put(f"/api/comment/{comment_id}/", data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_comment = Comment.objects.get(id=response.data["id"])
        self.post.refresh_from_db()
        self.assertEqual(updated_comment.user, updated_data["user"])
        self.assertEqual(updated_comment.content, updated_data["content"])

        comment_id1 = self.comment1.id

        response = self.client.put(f"/api/comment/{comment_id1}/", data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment(self):
        self.client.force_authenticate(self.user1)
        comment_id = self.comment.id
        response = self.client.delete(f"/api/comment/{comment_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        comment_id1 = self.comment1.id
        response = self.client.delete(f"/api/comment/{comment_id1}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comments_list(self):
        warnings.filterwarnings("ignore", category=UnorderedObjectListWarning)
        response = self.client.get(COMMENT_URL)
        comments_ids = [comment["id"] for comment in response.data["results"]]
        following_posts = Post.objects.filter(profile__in=self.profile.followings.all())
        user_posts = Post.objects.filter(profile=self.profile)
        all_posts = following_posts | user_posts
        comments = Comment.objects.filter(post__in=all_posts).order_by("id")
        comments_ids_ = list(comments.values_list("id", flat=True))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(comments_ids, comments_ids_)

    def test_create_postlike(self):
        post_id = self.post.id
        data = {"status": "UNLIKE"}
        response = self.client.post(f"/api/post/{post_id}/postlike/create/", data=data)
        created_postlike = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_postlike["status"], "UNLIKE")

    def test_posts_liked_list(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(reverse("app:liked-posts"))
        postlikes_ids = [postlike["id"] for postlike in response.data["results"]]
        postlikes = PostLike.objects.filter(
            author=self.user1, status=PostLike.StatusChoices.UNLIKE
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(postlikes), len(postlikes_ids))

        self.client.force_authenticate(self.user2)
        response = self.client.get(reverse("app:liked-posts"))
        postlikes_ids = [postlike["id"] for postlike in response.data["results"]]
        postlikes = PostLike.objects.filter(
            author=self.user2, status=PostLike.StatusChoices.LIKE
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(postlikes), len(postlikes_ids))
