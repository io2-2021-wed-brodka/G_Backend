from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from core.testcases import APITestCase
from users.models import User, UserRole, UserState


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
        self.assertDictEqual(request.data, {"message": "Username already taken."})

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
        self.assertDictEqual(request.data, {"message": "Invalid request."})


class LoginTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        # drop authentication done in APITestCase.setUp
        self.client.force_authenticate(user=None)

    def test_login_user_successful_status_code(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(
            username=username, password=password, role=UserRole.user
        )
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": password, "role": UserRole.user},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_successful_body(self):
        username = "john-doe"
        password = "qwerty"
        user = User.objects.create_user(
            username=username, password=password, role=UserRole.user
        )
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": password, "role": UserRole.user},
        )
        token, _ = Token.objects.get_or_create(user=user)
        self.assertDictEqual(
            response.data,
            {
                "token": token.key,
                "role": user.role,
            },
        )

    def test_login_fail_bad_credentials_status_code(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(
            username=username, password=password, role=UserRole.user
        )
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": "password", "role": UserRole.user},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fail_bad_credentials_body(self):
        username = "john-doe"
        password = "qwerty"
        User.objects.create_user(
            username=username, password=password, role=UserRole.user
        )
        response = self.client.post(
            reverse("login"),
            {"login": username, "password": "password", "role": UserRole.user},
        )
        self.assertDictEqual(response.data, {"message": "Bad credentials."})


class LogoutTestCase(APITestCase):
    def test_logout_user_successful_status_code(self):
        response = self.client.post(
            reverse("logout"),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_logout_unauthorized_body(self):
    #     # drop authentication done in APITestCase.setUp
    #     self.client.force_authenticate(user=None)
    #     response = self.client.post(
    #         reverse("logout"),
    #     )
    #     self.assertEqual(response.data, {"message": "Unauthorized."})


class UserListTestCase(APITestCase):
    def test_list_users_status_code(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_body(self):
        user1 = User.objects.create(username="user1", role=UserRole.user)
        user2 = User.objects.create(username="user2", role=UserRole.user)
        User.objects.create(username="tech1", role=UserRole.tech)
        User.objects.create(username="admin2", role=UserRole.admin)
        response = self.client.get(reverse("user-list"))
        self.assertDictEqual(
            response.data,
            {
                "users": [
                    {
                        "id": str(user1.id),
                        "name": str(user1.username),
                    },
                    {
                        "id": str(user2.id),
                        "name": str(user2.username),
                    },
                ],
            },
        )


class UserBlockedListTestCase(APITestCase):
    def test_list_blocked_users_status_code(self):
        response = self.client.get(reverse("users-blocked-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_body(self):
        User.objects.create(username="user0", role=UserRole.user)
        user1 = User.objects.create(
            username="user1", role=UserRole.user, state=UserState.blocked
        )
        user2 = User.objects.create(
            username="user2", role=UserRole.user, state=UserState.blocked
        )
        User.objects.create(username="user3", role=UserRole.user)
        response = self.client.get(reverse("users-blocked-list"))
        self.assertDictEqual(
            response.data,
            {
                "users": [
                    {
                        "id": str(user1.id),
                        "name": str(user1.username),
                    },
                    {
                        "id": str(user2.id),
                        "name": str(user2.username),
                    },
                ],
            },
        )


class UserBlockTestCase(APITestCase):
    def test_block_user_status_code(self):
        user = User.objects.create(username="user0", role=UserRole.user)
        response = self.client.post(reverse("users-blocked-list"), data={"id": user.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_block_user_body(self):
        user = User.objects.create(username="user0", role=UserRole.user)
        response = self.client.post(reverse("users-blocked-list"), data={"id": user.id})
        self.assertDictEqual(
            response.data,
            {
                "id": str(user.id),
                "name": str(user.username),
            },
        )

    def test_block_user_user_gets_blocked(self):
        user = User.objects.create(username="user0", role=UserRole.user)
        self.client.post(reverse("users-blocked-list"), data={"id": user.id})
        user.refresh_from_db()
        self.assertEqual(user.state, UserState.blocked)

    def test_block_user_fails_already_blocked_status_code(self):
        user = User.objects.create(
            username="user0", role=UserRole.user, state=UserState.blocked
        )
        response = self.client.post(reverse("users-blocked-list"), data={"id": user.id})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_block_user_fails_already_blocked_body(self):
        user = User.objects.create(
            username="user0", role=UserRole.user, state=UserState.blocked
        )
        response = self.client.post(reverse("users-blocked-list"), data={"id": user.id})
        self.assertEqual(response.data, {"message": "User already blocked."})


class UserUnblockTestCase(APITestCase):
    def test_unblock_user_status_code(self):
        user = User.objects.create(
            username="user0", role=UserRole.user, state=UserState.blocked
        )
        response = self.client.delete(
            reverse("users-blocked-detail", kwargs={"pk": user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unblock_user_body(self):
        user = User.objects.create(
            username="user0", role=UserRole.user, state=UserState.blocked
        )
        response = self.client.delete(
            reverse("users-blocked-detail", kwargs={"pk": user.id})
        )
        self.assertEqual(response.data, None)

    def test_unblock_user_user_gets_unblocked(self):
        user = User.objects.create(
            username="user0", role=UserRole.user, state=UserState.blocked
        )
        self.client.delete(reverse("users-blocked-detail", kwargs={"pk": user.id}))
        user.refresh_from_db()
        self.assertEqual(user.state, UserState.active)

    def test_unblock_user_fails_already_unblocked_status_code(self):
        user = User.objects.create(username="user0", role=UserRole.user)
        response = self.client.delete(
            reverse("users-blocked-detail", kwargs={"pk": user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_unblock_user_fails_already_unblocked_body(self):
        user = User.objects.create(username="user0", role=UserRole.user)
        response = self.client.delete(
            reverse("users-blocked-detail", kwargs={"pk": user.id})
        )
        self.assertEqual(response.data, {"message": "User not blocked."})


class TechCreateTestCase(APITestCase):
    def test_tech_create_status_code(self):
        response = self.client.post(
            reverse("tech-list"),
            data={"name": "tech0", "password": "p@ssw0rd!"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tech_create_body(self):
        username = "tech0"
        response = self.client.post(
            reverse("tech-list"),
            data={"name": username, "password": "p@ssw0rd!"},
        )
        user = User.objects.get(username=username)
        self.assertDictEqual(
            response.data,
            {
                "id": str(user.id),
                "name": username,
            },
        )


class TechGetTestCase(APITestCase):
    def test_get_tech_status_code(self):
        user = User.objects.create(
            username="user0", password="1234", role=UserRole.tech
        )
        response = self.client.get(reverse("tech-list"), kwargs={"pk": user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_wrong_tech_status_code(self):
        user = User.objects.create(
            username="user194", password="5678", role=UserRole.user
        )  # non-tech user
        response = self.client.get(reverse("tech-detail", kwargs={"pk": user.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_tech_body(self):
        user = User.objects.create(
            username="user0", password="1234", role=UserRole.tech
        )
        response = self.client.get(reverse("tech-detail", kwargs={"pk": user.id}))
        self.assertDictEqual(
            response.data,
            {
                "id": str(user.id),
                "name": str(user.username),
            },
        )


class TechListTestCase(APITestCase):
    def test_get_tech_list_status_code(self):
        response = self.client.get(reverse("tech-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_tech_list_body(self):
        user1 = User.objects.create(
            username="tech0", password="1234", role=UserRole.tech
        )
        user2 = User.objects.create(
            username="tech1", password="5678", role=UserRole.tech
        )
        User.objects.create(username="user0", password="5678", role=UserRole.user)
        response = self.client.get(reverse("tech-list"))
        self.assertDictEqual(
            response.data,
            {
                "techs": [
                    {
                        "id": str(user1.id),
                        "name": str(user1.username),
                    },
                    {
                        "id": str(user2.id),
                        "name": str(user2.username),
                    },
                ],
            },
        )


class TechDeleteTestCase(APITestCase):
    def test_delete_tech_status_code(self):
        user = User.objects.create(
            username="user0", password="1234", role=UserRole.tech
        )
        response = self.client.delete(reverse("tech-detail", kwargs={"pk": user.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_found_tech_status_code(self):
        user = User.objects.create(
            username="user194", password="5678", role=UserRole.user
        )  # non-tech user
        response = self.client.delete(reverse("tech-detail", kwargs={"pk": user.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
