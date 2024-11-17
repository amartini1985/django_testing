from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    form_data,
    url_detail
):
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client,
        author,
        news,
        form_data,
        url_detail
):
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        author_client,
        url_detail,
        bad_word
):
    response = author_client.post(url_detail, data=bad_word)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client,
        url_delete,
        url_detail
):
    comment_url = url_detail + '#comments'
    response = author_client.delete(url_delete)
    assertRedirects(response, comment_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        url_delete
):
    response = not_author_client.delete(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        form_data,
        url_edit,
        url_detail
):
    comment_url = url_detail + '#comments'
    response = author_client.post(url_edit, data=form_data)
    assertRedirects(response, comment_url)
    comment_from_bd = Comment.objects.get(id=comment.id)
    assert comment_from_bd.text == form_data['text']
    assert comment_from_bd.news == comment.news
    assert comment_from_bd.author == comment.author


def test_user_cant_edit_comment_of_another(
        not_author_client,
        comment,
        form_data,
        url_edit
):
    response = not_author_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_bd = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_bd.text
    assert comment.author == comment_from_bd.author
    assert comment.news == comment_from_bd.news
