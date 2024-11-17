from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseFixtures(TestCase):

    TEXT_NOTE = 'Текст заметки'
    TITLE_NOTE = 'Заголовок 1'
    TEXT_CHANGE = 'Текст заметки новый'
    TITLE_CHANGE = 'Заголовок 1 новый'
    SLUG = 'slug'
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    SUCCESS_URL = reverse('notes:success')
    EDIT_URL = reverse('notes:edit', args=(SLUG,))
    DELETE_URL = reverse('notes:delete', args=(SLUG,))
    DETAIL_URL = reverse('notes:detail', args=(SLUG,))

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User1')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='User2')
        cls.read_client = Client()
        cls.read_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE_NOTE,
            text=cls.TEXT_NOTE,
            slug=cls.SLUG,
            author=cls.author,)
        cls.form_data = {
            'title': cls.TITLE_CHANGE,
            'text': cls.TEXT_CHANGE,
            'slug': cls.SLUG,
            'author': cls.author,
        }
