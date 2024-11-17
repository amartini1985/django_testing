from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .fixtures import BaseFixtures, BaseFixturesWithoutNote


User = get_user_model()


class TestNotesCreation(BaseFixturesWithoutNote):

    def test_anonymous_user_cant_create_note(self):
        note_count_start = Note.objects.count()
        self.client.post(self.ADD_URL, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, note_count_start)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.form_data['author'])

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseFixtures):

    def test_author_can_delete_note(self):
        responce = self.auth_client.delete(self.DELETE_URL)
        self.assertRedirects(responce, self.SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        responce = self.read_client.delete(self.DELETE_URL)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        responce = self.auth_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(responce, self.SUCCESS_URL)
        note_from_bd = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_bd.title, self.form_data['title'])
        self.assertEqual(note_from_bd.text, self.form_data['text'])

    def test_reader_can_edit_note(self):
        responce = self.read_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        note_from_bd = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_bd.title, self.TITLE_NOTE)
        self.assertEqual(note_from_bd.text, self.TEXT_NOTE)

    def test_notes_matching_slug(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field=self.note.slug,
            errors=self.note.slug + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
