from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='ZSV3')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='NAT',
        )
        cls.post_obj = Post.objects.create(
            text='Тестовый текст 1',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_for_notauthorized_users(self) -> None:
        """Проверить доступность страниц для неавториз.пользователя."""
        url_statuscode = {
            reverse('posts:index'):
                HTTPStatus.OK,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                HTTPStatus.OK,
            reverse('posts:profile', kwargs={'username': self.user.username}):
                HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id}):
                HTTPStatus.OK,
            '/unexisting_page/':
                HTTPStatus.NOT_FOUND,
        }
        for address, statuscode in url_statuscode.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, statuscode)

    def test_url_exists_for_authorized_users(self) -> None:
        """Проверить доступность страниц для авториз.пользователя."""
        url_statuscode = {
            reverse('posts:index'):
                HTTPStatus.OK,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                HTTPStatus.OK,
            reverse('posts:profile', kwargs={'username': self.user.username}):
                HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id}):
                HTTPStatus.OK,
            reverse('posts:post_edit', kwargs={'post_id': self.post_obj.id}):
                HTTPStatus.OK,  # author = user
            reverse('posts:post_create'):
                HTTPStatus.OK,
            '/unexisting_page/':
                HTTPStatus.NOT_FOUND,
        }
        for address, statuscode in url_statuscode.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, statuscode)

    def test_template_exists_for_url_for_notauthorized_users(self):
        """Проверить доступность шаблона для страницы для неавториз.польз."""
        url_template = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id}):
                'posts/post_detail.html',
            '/unexisting_page/':
                'core/404.html',
        }
        for address, template in url_template.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_template_exists_for_url_for_authorized_users(self):
        """Проверить доступность шаблона для страницы для авториз.польз."""
        url_template = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post_obj.id}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }
        for address, template in url_template.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
