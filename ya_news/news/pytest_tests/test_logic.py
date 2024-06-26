from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_create_comment(
    author, author_client, comment_form_data, news, detail_url
):
    comments_before = set(Comment.objects.all())
    assertRedirects(
        author_client.post(detail_url, data=comment_form_data),
        f'{detail_url}#comments'
    )
    created_comments = set(Comment.objects.all()) - comments_before
    assert len(created_comments) == 1, 'No Comments!'
    comment = created_comments.pop()
    assert comment.text == comment_form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, comment_form_data, detail_url, login_url
):
    comments_before = set(Comment.objects.all())
    assertRedirects(
        client.post(detail_url, data=comment_form_data),
        f'{login_url}?next={detail_url}'
    )
    assert set(Comment.objects.all()) == comments_before


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    detail_url, admin_client, comment_form_data_with_bad_word
):
    comments_before = set(Comment.objects.all())
    assertFormError(
        admin_client.post(
            detail_url,
            data=comment_form_data_with_bad_word
        ),
        'form',
        'text',
        errors=WARNING
    )
    assert set(Comment.objects.all()) == comments_before


def test_author_can_delete_comment(
    delete_url, author_client, detail_url, comment
):
    count_comments_before_del = Comment.objects.count()
    assertRedirects(author_client.delete(delete_url), detail_url + '#comments')
    assert (count_comments_before_del - 1) == Comment.objects.count()
    assert Comment.objects.filter(pk=comment.pk).exists() is False


def test_user_cant_delete_comment_of_another_user(
    delete_url, admin_client, detail_url, comment
):
    comments_before_del = set(Comment.objects.all())
    assert admin_client.delete(delete_url).status_code == HTTPStatus.NOT_FOUND
    assert comments_before_del == set(Comment.objects.all())
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text
    assert comment_from_db.created == comment.created


def test_author_can_edit_comment(
    edit_url, author_client, comment_form_data, detail_url, comment
):
    assertRedirects(
        author_client.post(edit_url, data=comment_form_data),
        detail_url + '#comments'
    )
    comment_after_edit = Comment.objects.get(pk=comment.pk)
    assert comment_after_edit.text == comment_form_data['text']
    assert comment_after_edit.author == comment.author
    assert comment_after_edit.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    edit_url, admin_client, comment_form_data, comment
):
    assert admin_client.post(
        edit_url, data=comment_form_data
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text
    assert comment_from_db.created == comment.created
