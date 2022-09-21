from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='ZSV3')
        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='NAT',
        )
        cls.post_obj = Post.objects.create(
            text='Тестовый-2 текст 2',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_template_exists_for_name(self):
        """Проверить доступность шаблона для страницы по name."""
        name_template = {
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
        for reverse_item, template in name_template.items():
            with self.subTest(reverse_item=reverse_item):
                response = self.authorized_client.get(reverse_item)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом: тип поля."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # альтернативный вызов
                # form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_contains_correct_context(self):
        """Проверить: страница post_detail содержит correct контекст: value."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id})
        ))
        self.assertEqual(response.context['post'].author.username,
                         self.post_obj.author.username)
        self.assertEqual(response.context['post'].text,
                         self.post_obj.text)
        self.assertEqual(response.context['post'].group.title,
                         self.post_obj.group.title)

    def test_post_edit_page_contains_correct_context(self):
        """Проверить: страница post_edit содержит correct контекст: value."""
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post_obj.id})
        ))
        self.assertEqual(response.context['post_obj'].text,
                         self.post_obj.text)
        self.assertEqual(response.context['post_obj'].group,
                         self.post_obj.group)

    def test_post_create_page_contains_correct_context(self):
        """Проверить: страница post_create содержит correct контекст: None."""
        response = (self.authorized_client.get(
            reverse('posts:post_create')
        ))
        for form_item in response.context['form']:
            self.assertIsNone(form_item.value())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='ZSV3')
        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='NAT',
        )
        bulk_obj_range = 13
        bulk_obj = (
            Post(
                text=f'Тестовый-{i} текст {i}',
                author=cls.user,
                group=cls.group,
            ) for i in range(bulk_obj_range)
        )
        cls.post_obj = Post.objects.bulk_create(bulk_obj)

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        """Проверить: кол-во постов первой страницы index = 10."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_recordss(self):
        """Проверить: кол-во постов второй страницы index = 3."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_contains_ten_records(self):
        """Проверить: кол-во постов первой страницы group_list = 10."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_contains_three_records(self):
        """Проверить: кол-во постов первой страницы group_list = 3."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + '?page=2'
        ))
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        """Проверить: кол-во постов первой страницы profile = 10."""
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        """Проверить: кол-во постов первой страницы profile = 3."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + '?page=2'
        ))
        self.assertEqual(len(response.context['page_obj']), 3)
