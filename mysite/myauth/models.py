from django.contrib.auth.models import User
from django.db import models


def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return 'profiles/profile_{pk}/avatar/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(blank=True, null=True, upload_to=profile_avatar_directory_path)

    def __str__(self) -> str:
        return f"Profile ( pk= {self.pk}, name= {self.user.username!r})"
