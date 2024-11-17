from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .fixtures import BaseFixtures

User = get_user_model()


class TestContent(BaseFixtures):

    def test_notes_list_for_different_users(self):
        data = (
            (self.auth_client, True),
            (self.read_client, False),
        )
        for name, result in data:
            with self.subTest(name=name):
                response = name.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), result)

    def test_authorized_client_has_form(self):
        urls = (self.ADD_URL, self.EDIT_URL)
        for url in urls:
            with self.subTest(name=url):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
