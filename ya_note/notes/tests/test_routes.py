from http import HTTPStatus

from django.contrib.auth import get_user_model

from .fixtures import BaseFixtures

User = get_user_model()


class TestRoutes(BaseFixtures):

    def test_page_availability_for_anonymous_user(self):
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_availability_for_author(self):
        urls = (
            self.DETAIL_URL,
            self.EDIT_URL,
            self.DELETE_URL
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        users_statuses = (
            (self.auth_client, HTTPStatus.OK),
            (self.read_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (self.DETAIL_URL, self.EDIT_URL, self.DELETE_URL):
                with self.subTest(user=user, name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.DETAIL_URL,
            self.EDIT_URL,
            self.DELETE_URL,
            self.LIST_URL,
            self.SUCCESS_URL,
            self.ADD_URL
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
