from core.testcases import APITestCase
from rest_framework.authtoken.models import Token

from rest_framework.reverse import reverse
from rest_framework import status

from users.models import User, UserRole


class RegisterTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        # drop authentication done in APITestCase.setUp
        self.client.force_authenticate(user=None)

    def test_register_successful_status_code(self):
        response = self.client.post(
            reverse("register"), {"login": "john-doe", "password": "qwerty"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_successful_body(self):
        username = "john-doe"
        response = self.client.post(
            reverse("register"), {"login": username, "password": "qwerty"}
        )
        user = User.objects.get(username=username)
        token = Token.objects.get(user=user)
        self.assertDictEqual(response.data, {"token": token.key})

    def test_register_successful_user_created(self):
        username = "john-doe"
        self.client.post(reverse("register"), {"login": username, "password": "qwerty"})
        user = User.objects.get(username=username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)
        self.assertEqual(user.role, UserRole.user)

    def test_register_fail_username_taken_status_code(self):
        username = "john-doe"
        User.objects.create_user(username=username, password="qwerty")
        request = self.client.post(
            reverse("register"), {"login": username, "password": "qwerty"}
        )
        self.assertEqual(request.status_code, status.HTTP_409_CONFLICT)

    def test_register_fail_username_taken_body(self):
        username = "john-doe"
        User.objects.create_user(username=username, password="qwerty")
        request = self.client.post(
            reverse("register"), {"login": username, "password": "qwerty"}
        )
        self.assertDictEqual(request.data, {"message": "username already taken"})

    def test_register_fail_no_username_status_code(self):
        username = "john-doe"
        User.objects.create_user(username=username, password="qwerty")
        request = self.client.post(
            reverse("register"), {"login": "", "password": "qwerty"}
        )
        self.assertEqual(request.status_code, status.HTTP_409_CONFLICT)

    def test_register_fail_no_username_body(self):
        username = "john-doe"
        User.objects.create_user(username=username, password="qwerty")
        request = self.client.post(
            reverse("register"), {"login": "", "password": "qwerty"}
        )
        self.assertDictEqual(request.data, {"message": "invalid request"})


class LoginTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        # drop authentication done in APITestCase.setUp
        self.client.force_authenticate(user=None)

    def test_login_user_successful_status_code(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(username=username, password=password, role="user")
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": password, "role": "user"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_successful_body(self):
        username = "john-doe"
        password = "qwerty"
        user = User.objects.create_user(
            username=username, password=password, role="user"
        )
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": password, "role": "user"},
        )
        token, _ = Token.objects.get_or_create(user=user)
        self.assertDictEqual(response.data, {"token": token.key})

    def test_login_fail_bad_credentials_status_code(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(username=username, password=password, role="user")
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": "password", "role": "user"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fail_bad_credentials_body(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(username=username, password=password, role="user")
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": "password", "role": "user"},
        )
        self.assertDictEqual(response.data, {"message": "bad credentials"})


class LogoutTestCase(APITestCase):
    def test_logout_user_successful_status_code(self):
        response = self.client.post(
            reverse("logout"),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_successful_body(self):
        response = self.client.post(
            reverse("logout"),
        )
        self.assertEqual(response.data, {"message": "Successfully logged out."})

    def test_logout_unauthorized_status_code(self):
        # drop authentication done in APITestCase.setUp
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("logout"),
        )
        # TODO(tkarwowski): revisit after logout is officially in specification
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # TODO(tkarwowski): revisit after logout is officially in specification
    # def test_logout_unauthorized_body(self):
    #     # drop authentication done in APITestCase.setUp
    #     self.client.force_authenticate(user=None)
    #     response = self.client.post(
    #         reverse("logout"),
    #     )
    #     self.assertEqual(response.data, {"message": "Invalid token."})
