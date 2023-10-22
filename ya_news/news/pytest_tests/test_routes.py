from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('id_for_news')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
    )
)
def test_pages_availability(client, name, args):
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
        id_for_comment, parametrized_client, expected_status, name
):
    assert parametrized_client.get(
        reverse(name, args=id_for_comment)
    ).status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, id_for_comment):
    url = reverse(name, args=id_for_comment)
    assertRedirects(client.get(url), f'{reverse("users:login")}?next={url}')
