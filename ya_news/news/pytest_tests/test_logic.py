from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_create_comment(
    author, author_client, form_data, news, detail_url
):
    assertRedirects(
        author_client.post(detail_url, data=form_data),
        f'{detail_url}#comments'
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(detail_url, client, form_data):
    assertRedirects(
        client.post(detail_url, data=form_data),
        f'{reverse("users:login")}?next={detail_url}'
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(detail_url, admin_client):
    assertFormError(
        admin_client.post(
            detail_url,
            data={'text': f'Text, {BAD_WORDS[0]}, etc'}
        ),
        'form',
        'text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(delete_url, author_client, detail_url):
    assertRedirects(author_client.delete(delete_url), detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    delete_url, admin_client
):
    assert admin_client.delete(delete_url).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    edit_url, author_client, form_data, detail_url, comment
):
    assertRedirects(
        author_client.post(edit_url, data=form_data),
        detail_url + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    edit_url, admin_client, form_data, comment
):
    assert admin_client.post(
        edit_url, data=form_data
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
