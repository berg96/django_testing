from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
ANONYMOUS = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('admin_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, ANONYMOUS, HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, redirect_url',
    (
        (EDIT_URL, f'{LOGIN_URL}?next={EDIT_URL}'),
        (DELETE_URL, f'{LOGIN_URL}?next={DELETE_URL}'),
    )
)
def test_redirect_for_anonymous_client(client, url, redirect_url):
    print(client.get(url).url)
    print(redirect_url)
    assertRedirects(client.get(url), redirect_url)
