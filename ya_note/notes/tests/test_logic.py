from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotesCreation(TestCase):
    TITLE = 'Заголовок 1'
    TEXT = 'Текст 1'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User1')
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user,
        }
        cls.form_data_2 = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)

    def test_notes_matching_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.auth_client.post(self.url, data=self.form_data_2)
        note = Note.objects.get()
        self.assertFormError(
            response,
            form='form',
            field=note.slug,
            errors=note.slug + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    TEXT_NOTE = 'Текст заметки'
    TEXT_CHANGE = 'Текст заметки новый'
    TITLE = 'Заголовок 1'
    TITLE_CHANGE = 'Заголовок 1 новый'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User_1')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='User_2')
        cls.read_client = Client()
        cls.read_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок 1',
            text=cls.TEXT_NOTE,
            slug='slug',
            author=cls.author
        )
        cls.url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_done = reverse('notes:success')
        cls.form_data = {'title': cls.TITLE_CHANGE, 'text': cls.TEXT_CHANGE}

    def test_author_can_delete_note(self):
        responce = self.auth_client.delete(self.url_delete)
        self.assertRedirects(responce, self.url_done)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        responce = self.read_client.delete(self.url_delete)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        responce = self.auth_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(responce, self.url_done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT_CHANGE)

    def test_reader_can_edit_note(self):
        responce = self.read_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT_NOTE)
