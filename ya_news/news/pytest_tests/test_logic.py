from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')


@pytest.mark.django_db
@pytest.mark.parametrize('url', (DETAIL_URL,))
def test_user_can_create_comment(
    author, author_client, form_data_for_comment, news, url
):
    comments_before = author_client.get(
        url
    ).context['news'].comment_set.all()
    assertRedirects(
        author_client.post(url, data=form_data_for_comment),
        f'{url}#comments'
    )
    comments_after = author_client.get(
        url
    ).context['news'].comment_set.all()
    created_comment = set(comments_after) - set(comments_before)
    assert created_comment, 'No Comments!'
    comment = Comment.objects.get(id=created_comment.pop().id)
    assert comment.text == form_data_for_comment['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, log_url',
    ((DETAIL_URL, LOGIN_URL),)
)
def test_anonymous_user_cant_create_comment(
    client, form_data_for_comment, url, log_url
):
    comments_before_post = client.get(url).context['news'].comment_set.all()
    assertRedirects(
        client.post(url, data=form_data_for_comment),
        f'{log_url}?next={url}'
    )
    comments_after_post = client.get(url).context['news'].comment_set.all()
    assert set(comments_after_post) == set(comments_before_post)


@pytest.mark.django_db
@pytest.mark.parametrize('url', (DETAIL_URL,))
def test_user_cant_use_bad_words(
    url, admin_client, form_data_for_comment_with_bad_word
):
    comments_before_post = admin_client.get(
        url
    ).context['news'].comment_set.all()
    assertFormError(
        admin_client.post(
            url,
            data=form_data_for_comment_with_bad_word
        ),
        'form',
        'text',
        errors=WARNING
    )
    comments_after_post = admin_client.get(
        url
    ).context['news'].comment_set.all()
    assert set(comments_after_post) == set(comments_before_post)


@pytest.mark.parametrize('del_url, det_url', ((DELETE_URL, DETAIL_URL), ))
def test_author_can_delete_comment(del_url, author_client, det_url):
    comments_before_del = author_client.get(
        det_url
    ).context['news'].comment_set.all()
    assertRedirects(author_client.delete(del_url), det_url + '#comments')
    comments_after_del = author_client.get(
        det_url
    ).context['news'].comment_set.all()
    assert set(comments_before_del) - set(comments_after_del)


@pytest.mark.parametrize('del_url, det_url', ((DELETE_URL, DETAIL_URL), ))
def test_user_cant_delete_comment_of_another_user(
    del_url, admin_client, det_url, comment
):
    comments_before_del = admin_client.get(
        det_url
    ).context['news'].comment_set.all()
    assert admin_client.delete(del_url).status_code == HTTPStatus.NOT_FOUND
    comments_after_del = admin_client.get(
        det_url
    ).context['news'].comment_set.all()
    assert set(comments_after_del) == set(comments_before_del)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text
    assert comment_from_db.created == comment.created


@pytest.mark.parametrize('ed_url, det_url', ((EDIT_URL, DETAIL_URL), ))
def test_author_can_edit_comment(
    ed_url, author_client, form_data_for_comment,
    det_url, comment, author, news
):
    assertRedirects(
        author_client.post(ed_url, data=form_data_for_comment),
        det_url + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data_for_comment['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('ed_url', (EDIT_URL, ))
def test_user_cant_edit_comment_of_another_user(
    ed_url, admin_client, form_data_for_comment, comment
):
    assert admin_client.post(
        ed_url, data=form_data_for_comment
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text
    assert comment_from_db.created == comment.created
