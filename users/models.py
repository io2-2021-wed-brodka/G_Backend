from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
