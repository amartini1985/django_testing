from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_home'),
        pytest.lazy_fixture('url_login'),
        pytest.lazy_fixture('url_logout'),
        pytest.lazy_fixture('url_signup'),
        pytest.lazy_fixture('url_detail'),
    ),
)
def test_pages_availability(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_edit'),
        pytest.lazy_fixture('url_delete'),
    ),
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
    (
        pytest.lazy_fixture('url_edit'),
        pytest.lazy_fixture('url_delete'),
    ),
)
def test_redirect_for_anonymous_client(client, url, url_login):
    redirect_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
