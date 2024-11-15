from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoute(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user1')
        cls.reader = User.objects.create(username='Reader')
        cls.notes = Note.objects.create(
            title='Заголовок 1',
            text='Текст заметки 1',
            slug='notes_slug',
            author=cls.author,
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_page_availability_for_anonymous_user(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_availability_for_author(self):
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
