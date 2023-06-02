import os
import uuid

from django.conf import settings
from functools import partial
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from user.models import User


def post_image_file_path(folder, instance, filename):
    _, extention = os.path.splitext(filename)
    filename = f"{instance.slug}-{uuid.uuid4()}.{extention}"
    return os.path.join(f"uploads/{folder}/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(max_length=63, blank=False, unique=True)
    avatar = models.ImageField(
        "Avatar", blank=True, null=True, upload_to=partial(post_image_file_path, "profiles")
    )
    city = models.CharField(max_length=63, blank=True, null=True)
    birth_date = models.CharField(max_length=63, blank=True, null=True)
    following = models.ManyToManyField(
        "self", related_name="followings", symmetrical=False
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username

    @property
    def followings_count(self):
        return self.followings.count()


class Post(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(blank=True, null=True,
                              upload_to=partial(post_image_file_path, "posts"))
    video = models.FileField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=250, unique=True)
    likes = models.ManyToManyField(User, through="PostLike", related_name="likes")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        counter = 1

        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{counter}"
            counter += 1

        return unique_slug

    def get_like_count(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


class PostLike(models.Model):
    class StatusChoices(models.TextChoices):
        LIKE = "LIKE"
        UNLIKE = "UNLIKE"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="postlikes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postlikes")
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices)

    class Meta:
        unique_together = ("author", "post")
