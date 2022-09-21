import shutil
import tempfile
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='ZSV3')
        cls.group = Group.objects.create(
            title='Тестовая группа 3',
            slug='NAT',
        )
        cls.post_obj = Post.objects.create(
            text='Тестовый-3 текст 3',
            author=cls.user,
            group=cls.group,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def setUp(self) -> None:
        """Создать клиент, point_to_disk."""
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()

    def tearDown(self) -> None:
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_newrecord_by_sendform(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'ВТОРАЯ запись поста zsv',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(
            response.context.get('page_obj')[0].image, 'posts/small.gif')

    def test_edit_existsrecord_by_sendform(self):
        post_count = Post.objects.count()
        form_data = {
            'text': f'EDIT_1 + {self.post_obj.text} + EDIT_1',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response_post = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post_obj.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif'
                # image=form_data['image'] -> don't work( why?
                # how to concatenate? upload_to='posts/' and form_data['image']
                # how to invoke?: <object>.upload_to
            ).exists()
        )
        self.assertRedirects(
            response_post,
            reverse('posts:post_detail', kwargs={'post_id': self.post_obj.id})
        )
        self.assertEqual(
            response_post.context['post'].text, form_data['text'])
        self.assertEqual(
            response_post.context['post'].group.id, form_data['group'])
        self.assertEqual(
            response_post.context['post'].image, 'posts/small.gif')

    def test_show_image_in_page_by_context(self):
        form_data = {
            'text': 'ЧЕТВЕРТАЯ запись поста zsv',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response_post = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response_get = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': response_post.context.get('page_obj')[0].id}
            )
        )
        self.assertEqual(
            response_get.context['post'].image, 'posts/small.gif'
        )
        reverse_context = {
            reverse('posts:index'):
                'post_list',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'page_obj',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'page_obj',
        }
        for reverse_item, context_item in reverse_context.items():
            with self.subTest(reverse_item=reverse_item):
                response_get = self.authorized_client.get(reverse_item)
                self.assertEqual(
                    response_get.context.get(context_item)[0].image,
                    'posts/small.gif'
                )

    def test_comment_by_authorized_user(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий номер 1',
            'author': self.user,
            'post': self.post_obj,
        }
        response_post = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_obj.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=form_data['author'],
                post=form_data['post'],
            ).exists()
        )
        self.assertEqual(
            response_post.context.get('comments')[0].text,
            form_data['text']
        )

    def test_comment_by_notauthorized_user(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий номер 2',
            'author': self.user,
            'post': self.post_obj,
        }
        response_post = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_obj.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertIsNone(response_post.context.get('comments'))


class PostCacheTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user('ZSV4')
        cls.post_obj = Post.objects.create(
            author=cls.user,
            text='ШЕСТАЯ запись'
        )

    def test_cache_in_index_page(self):
        response_get_1 = self.client.get(reverse('posts:index'))
        content_before_del = len(response_get_1.content)
        count_before_del = Post.objects.count()

        self.post_obj.delete()

        self.assertEqual(count_before_del - 1, Post.objects.count())

        # obj exists in_content_of_cache: all time of CACHE_PERIOD
        time.sleep(settings.CACHE_PERIOD - 1)
        response_get_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(content_before_del, len(response_get_2.content))

        # первая секунда после обновления кеша - и контент меняется
        time.sleep(1)
        response_get_3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(content_before_del, len(response_get_3.content))


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user('ZSV5')
        cls.user2 = User.objects.create_user('ZSV6')
        cls.user3 = User.objects.create_user('ZSV7')
        cls.post = Post.objects.create(
            text='Тестовый-5 текст-5',
            author=cls.user1,
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user1,
        )
        cls.follow_count = Follow.objects.count()

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_add_follow_by_authorized_user(self):
        response_get = self.authorized_client2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user3})
        )
        self.assertEqual(
            Follow.objects.count(), self.follow_count + 1
        )
        self.assertEqual(
            response_get.context.get('following'), True
        )
        self.assertEqual(
            response_get.context.get('author'), self.user3
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user2,
                author=self.user3
            ).exists()
        )

    def test_del_follow_by_authorized_user(self):
        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user1})
        )
        self.assertEqual(
            Follow.objects.count(), self.follow_count - 1
        )

    def test_show_post_in_follow_of_user(self):
        # 1.authorized user, who has follow
        response_get2 = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        self.assertTrue(
            response_get2.context.get('page_obj')
        )
        self.assertEqual(
            response_get2.context.get('page_obj')[0].text,
            self.post.text
        )

        # 2.authorized user, who don't have follow
        response_get1 = self.authorized_client1.get(
            reverse('posts:follow_index')
        )
        self.assertFalse(
            response_get1.context.get('page_obj')
        )

        # 3.not authorized user
        response_get = self.client.get(
            reverse('posts:follow_index')
        )
        self.assertFalse(
            response_get.context
        )
