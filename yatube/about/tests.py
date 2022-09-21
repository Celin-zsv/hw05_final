from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutUrlTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='ZSV3')
        self.authorized_client.force_login(self.user)

    def test_name_exists_for_notauthorized_users(self) -> None:
        """Проверить доступность страниц для неавториз.пользователя."""
        name_statuscode = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for reverse_item, statuscode in name_statuscode.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.guest_client.get(reverse_item)
                self.assertEqual(response.status_code, statuscode)

    def test_name_exists_for_authorized_users(self) -> None:
        """Проверить доступность страниц для авториз.пользователя."""
        name_statuscode = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for reverse_item, statuscode in name_statuscode.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.authorized_client.get(reverse_item)
                self.assertEqual(response.status_code, statuscode)

    def test_name_exists_for_template(self):
        """Проверить доступность шаблона для страницы по name."""
        name_template = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_item, template in name_template.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.authorized_client.get(reverse_item)
                self.assertTemplateUsed(response, template)
