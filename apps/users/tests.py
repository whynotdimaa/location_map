from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class UserFunctionalTests(APITestCase):
    def setUp(self):
        # Додано префікс users:
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.me_url = reverse('users:me')
        self.user = User.objects.create_user(username="existing", email="ex@mail.com", password="password123")

    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "new@mail.com",
            "password": "strongpassword123",
            "password_confirm": "strongpassword123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        data = {
            "username": "baduser",
            "email": "bad@mail.com",
            "password": "password123",
            "password_confirm": "differentpassword"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_duplicate_email(self):
        data = {
            "username": "anotheruser",
            "email": "ex@mail.com",
            "password": "password123",
            "password_confirm": "password123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_get_me_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "existing")

    def test_login_invalid_credentials(self):
        data = {"username": "existing", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        # Використовуємо прямий URL, щоб уникнути проблем з reverse
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "password123",
            "new_password": "new_strong_pass1",
            "new_password_confirm": "new_strong_pass1"
        }
        response = self.client.post('/api/auth/me/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Перевіряємо, що пароль дійсно змінився
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_strong_pass1"))