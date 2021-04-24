from django.test import TestCase
from rest_framework.authtoken.models import Token

from rest_framework.test import APIClient

from users.models import User, UserRole


class APITestCase(TestCase):
    def setUp(self):
        super().setUp()
        # help for debugging
        self.maxDiff = None

        self.user = User.objects.create_user(
            username="john", password="john", role=UserRole.admin
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        # TODO(tkarwowski): I wish we could do this the proper way with .configure, but it doesn't work
        self.client.force_authenticate(user=self.user)
