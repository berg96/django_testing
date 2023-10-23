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


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (DETAIL_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (EDIT_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (DELETE_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (EDIT_URL, pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (DELETE_URL, pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, log_url',
    (
        (EDIT_URL, LOGIN_URL),
        (DELETE_URL, LOGIN_URL),
    )
)
def test_redirect_for_anonymous_client(client, url, log_url):
    assertRedirects(client.get(url), f'{log_url}?next={url}')
