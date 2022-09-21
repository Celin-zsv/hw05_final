from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersUrlTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='ZSV3')
        self.authorized_client.force_login(self.user)

    def test_url_exists_for_notauthorized_users_v(self) -> None:
        """Проверить доступность страниц для неавториз.пользователя."""
        url_statuscode = {
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'NQ', 'token': '633-62d0a82df63b0c5d7099'}
            ): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
        }
        for address, statuscode in url_statuscode.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, statuscode)

    def test_url_exists_for_authorized_users(self) -> None:
        """Проверить доступность страниц для авториз.пользователя."""
        url_statuscode = {
            reverse('users:password_change_form'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
        }
        for address, statuscode in url_statuscode.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, statuscode)

    def test_template_exists_for_name_for_url_notauthorized_user(self):
        """Проверить доступность шаблона для стр. по name для неавтор.польз."""
        name_template = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'NQ', 'token': '633-62d0a82df63b0c5d7099'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for reverse_item, template in name_template.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.guest_client.get(reverse_item)
                self.assertTemplateUsed(response, template)

    def test_template_exists_for_name_for_url_authorized_user(self):
        """Проверить доступность шаблона для стр. по name для автор.польз."""
        name_template = {
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
        }
        for reverse_item, template in name_template.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.authorized_client.get(reverse_item)
                self.assertTemplateUsed(response, template)

    def test_create_newrecord_by_sendform(self):
        post_count = User.objects.count()
        pwd = ('=?utf-8?b?0KHQsdGA0L7RgSDQv9Cw0YDQvtC70'
               'Y8g0L3QsCAxMjcuMC4wLjE6ODAwMA==?=')
        form_data = {
            'username': 'ZSV4',
            'email': 'svzelenkovskii@gmail.com',
            'password1': pwd,
            'password2': pwd,
            'is_staff': True,
            'is_active': True,
            'is_superuser': True,
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), post_count + 1)
        self.assertTrue(
            User.objects.filter(
                username=form_data['username'],
                email=form_data['email'],
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
