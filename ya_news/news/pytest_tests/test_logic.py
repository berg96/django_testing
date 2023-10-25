from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_create_comment(
    author, author_client, comment_form_data, news, detail_url
):
    comments_before_set = set(Comment.objects.all())
    assertRedirects(
        author_client.post(detail_url, data=comment_form_data),
        f'{detail_url}#comments'
    )
    comments_after_set = set(Comment.objects.all())
    created_comments = comments_after_set - comments_before_set
    assert len(created_comments) == 1, 'No Comments!'
    comment = created_comments.pop()
    assert comment.text == comment_form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, comment_form_data, detail_url, login_url
):
    comments_before_post_set = set(Comment.objects.all())
    assertRedirects(
        client.post(detail_url, data=comment_form_data),
        f'{login_url}?next={detail_url}'
    )
    comments_after_post_set = set(Comment.objects.all())
    assert comments_after_post_set == comments_before_post_set


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    detail_url, admin_client, comment_form_data_with_bad_word
):
    comments_before_post_set = set(Comment.objects.all())
    assertFormError(
        admin_client.post(
            detail_url,
            data=comment_form_data_with_bad_word
        ),
        'form',
        'text',
        errors=WARNING
    )
    comments_after_post_set = set(Comment.objects.all())
    assert comments_after_post_set == comments_before_post_set


def test_author_can_delete_comment(delete_url, author_client, detail_url):
    count_comments_before_del = Comment.objects.count()
    assertRedirects(author_client.delete(delete_url), detail_url + '#comments')
    count_comments_after_del = Comment.objects.count()
    assert (count_comments_before_del - 1) == count_comments_after_del


def test_user_cant_delete_comment_of_another_user(
    delete_url, admin_client, detail_url, comment
):
    comments_before_del_set = set(Comment.objects.all())
    assert admin_client.delete(delete_url).status_code == HTTPStatus.NOT_FOUND
    comments_after_del = set(Comment.objects.all())
    assert comments_before_del_set == comments_after_del
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text
    assert comment_from_db.created == comment.created


def test_author_can_edit_comment(
    edit_url, author_client, comment_form_data, detail_url, comment
):
    comment_before_edit = comment
    assertRedirects(
        author_client.post(edit_url, data=comment_form_data),
        detail_url + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']
    assert comment.author == comment_before_edit.author
    assert comment.news == comment_before_edit.news


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
