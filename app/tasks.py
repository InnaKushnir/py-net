
from app.models import Post, Profile, User
from celery import shared_task

TITLE = "TEST!!!"
CONTENT = "Test Post"
USER_ID = 2


@shared_task
def create_post() -> int:
    user = User.objects.get(id=USER_ID)
    profile = Profile.objects.get(user=user)
    return Post.objects.create(owner=user, title=TITLE, content=CONTENT, profile=profile)
