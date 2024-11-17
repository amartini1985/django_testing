from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

URL_HOME = pytest.lazy_fixture('url_home')
URL_LOGIN = pytest.lazy_fixture('url_login')
URL_LOGOUT = pytest.lazy_fixture('url_logout')
URL_SIGNUP = pytest.lazy_fixture('url_signup')
URL_DETAIL = pytest.lazy_fixture('url_detail')
URL_EDIT = pytest.lazy_fixture('url_edit')
URL_DELETE = pytest.lazy_fixture('url_delete')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (URL_HOME, URL_LOGIN, URL_LOGOUT, URL_SIGNUP, URL_DETAIL),
)
def test_pages_availability(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (URL_EDIT, URL_DELETE),
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, url
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (URL_EDIT, URL_DELETE),
)
def test_redirect_for_anonymous_client(client, url, url_login):
    redirect_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
